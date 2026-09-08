interface Env {
  SPOTIFY_CLIENT_ID: string;
  SPOTIFY_CLIENT_SECRET: string;
  SPOTIFY_REFRESH_TOKEN: string;
}

type SpotifyTrack = {
  name: string;
  artists: Array<{ name: string }>;
  album: { images: Array<{ url: string }> };
  external_urls: { spotify: string };
};

const json = (value: unknown, status = 200) => Response.json(value, {
  status,
  headers: { "Cache-Control": status === 200 ? "private, max-age=30" : "no-store" },
});

async function accessToken(env: Env): Promise<string> {
  if (!env.SPOTIFY_CLIENT_ID || !env.SPOTIFY_CLIENT_SECRET || !env.SPOTIFY_REFRESH_TOKEN) {
    throw new Error("Spotify credentials are not configured");
  }
  const credentials = btoa(`${env.SPOTIFY_CLIENT_ID}:${env.SPOTIFY_CLIENT_SECRET}`);
  const response = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: { Authorization: `Basic ${credentials}`, "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "refresh_token", refresh_token: env.SPOTIFY_REFRESH_TOKEN }),
  });
  if (!response.ok) throw new Error(`Spotify token request failed: ${response.status}`);
  return ((await response.json()) as { access_token: string }).access_token;
}

function trackResponse(track: SpotifyTrack, isPlaying: boolean) {
  return {
    isPlaying,
    title: track.name,
    artist: track.artists.map((artist) => artist.name).join(", "),
    albumImageUrl: track.album.images[0]?.url ?? "",
    songUrl: track.external_urls.spotify,
  };
}

export const onRequestGet: PagesFunction<Env> = async ({ env }) => {
  try {
    const token = await accessToken(env);
    const headers = { Authorization: `Bearer ${token}` };
    const current = await fetch("https://api.spotify.com/v1/me/player/currently-playing", { headers });
    if (current.status === 200) {
      const payload = await current.json() as { is_playing: boolean; item?: SpotifyTrack };
      if (payload.is_playing && payload.item) return json(trackResponse(payload.item, true));
    }
    const recent = await fetch("https://api.spotify.com/v1/me/player/recently-played?limit=1", { headers });
    if (!recent.ok) throw new Error(`Spotify recent request failed: ${recent.status}`);
    const payload = await recent.json() as { items: Array<{ track: SpotifyTrack }> };
    return payload.items[0] ? json(trackResponse(payload.items[0].track, false)) : json({ isPlaying: false });
  } catch (error) {
    console.error(error);
    return json({ error: "Could not connect to Spotify." }, 502);
  }
};
