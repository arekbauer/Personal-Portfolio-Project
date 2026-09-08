import { TEAM_MAP } from "../../worker-lib/teams";

type VlrItem = {
  utc?: string;
  timestamp?: number;
  ago?: string;
  status?: string;
  tournament?: string;
  event?: string;
  teams?: Array<{ name: string; score?: number | string }>;
};

const WHITELIST = ["VCT 2026", "Valorant Masters", "Valorant Masters London 2026"];

async function getItems(url: string): Promise<VlrItem[]> {
  try {
    const response = await fetch(url, { cf: { cacheTtl: 60, cacheEverything: true } });
    if (!response.ok) return [];
    return ((await response.json()) as { data?: VlrItem[] }).data ?? [];
  } catch { return []; }
}

function londonDate(offsetDays = 0) {
  const date = new Date(Date.now() + offsetDays * 86_400_000);
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/London", year: "numeric", month: "2-digit", day: "2-digit" }).format(date);
}

function normalize(item: VlrItem) {
  const [first = { name: "TBD" }, second = { name: "TBD" }] = item.teams ?? [];
  const time = item.timestamp
    ? new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", hour: "numeric", minute: "2-digit", hour12: true }).format(new Date((item.timestamp + 4 * 3600) * 1000)).toLowerCase().replace(/^0/, "")
    : "";
  return {
    t1: TEAM_MAP[first.name] ?? first.name, s1: first.score,
    t2: TEAM_MAP[second.name] ?? second.name, s2: second.score,
    tournament: (item.tournament ?? "").replace("VCT 2026", "").replace(":", "").trim(),
    event: item.event, status: item.status, time,
  };
}

export const onRequestGet: PagesFunction = async () => {
  const [matches, results] = await Promise.all([
    getItems("https://vlr.orlandomm.net/api/v1/matches"),
    getItems("https://vlr.orlandomm.net/api/v1/results?page=1"),
  ]);
  const allowed = (item: VlrItem) => WHITELIST.some((name) => (item.tournament ?? "").includes(name));
  const payload = { live: [] as unknown[], t_up: [] as unknown[], tom_up: [] as unknown[], y_res: [] as unknown[], t_res: [] as unknown[] };
  for (const item of matches.filter(allowed)) {
    if ((item.utc ?? "").includes(londonDate())) (item.status ?? "").toUpperCase() === "LIVE" ? payload.live.push(normalize(item)) : payload.t_up.push(normalize(item));
    else if ((item.utc ?? "").includes(londonDate(1))) payload.tom_up.push(normalize(item));
  }
  for (const item of results.filter(allowed)) {
    if (!(item.ago ?? "").includes("d")) payload.t_res.push(normalize(item));
    else if ((item.ago ?? "").includes("1d")) payload.y_res.push(normalize(item));
  }
  return Response.json({ ...payload, last_updated: new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date()) });
};
