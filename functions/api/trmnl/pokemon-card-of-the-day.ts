interface Env { POKEMON_TCG_API_KEY?: string }

const RARITIES: Record<string, string[]> = {
  high_tier: ["Illustration Rare", "Special Illustration Rare", "Hyper Rare", "Shiny Rare", "Shiny Ultra Rare", "Rare Secret", "Rare Rainbow", "Rare Shiny", "Rare Shiny GX", "Rare Shining", "Amazing Rare"],
  illustration_rare: ["Illustration Rare"],
  special_illustration_rare: ["Special Illustration Rare"],
  sir_plus: ["Special Illustration Rare", "Hyper Rare", "Shiny Ultra Rare", "Rare Secret", "Rare Rainbow", "Rare Shiny GX", "Rare Shining"],
};

function hash(value: string): number {
  let result = 2166136261;
  for (const character of value) result = Math.imul(result ^ character.charCodeAt(0), 16777619);
  return result >>> 0;
}

function londonDateParts() {
  const parts = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", day: "2-digit", month: "short", year: "numeric" }).formatToParts(new Date());
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find((item) => item.type === type)?.value ?? "";
  return { key: `${part("year")}-${String(new Date(`${part("month")} 1, 2000`).getMonth() + 1).padStart(2, "0")}-${part("day")}`, display: `${part("day")} ${part("month")} ${part("year")}` };
}

function marketPrice(prices: Record<string, { market?: number }> = {}) {
  for (const type of ["holofoil", "normal", "reverseHolofoil", "1stEditionHolofoil", "1stEditionNormal"]) {
    if (prices[type]?.market != null) return prices[type].market;
  }
  return null;
}

async function cards(params: URLSearchParams, apiKey?: string) {
  const response = await fetch(`https://api.pokemontcg.io/v2/cards?${params}`, {
    headers: apiKey ? { "X-Api-Key": apiKey } : {},
    cf: { cacheTtl: 3600, cacheEverything: true },
  });
  if (!response.ok) throw new Error(`Pokémon TCG request failed: ${response.status}`);
  return response.json() as Promise<{ data?: Record<string, any>[]; totalCount?: number }>;
}

export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  const tier = new URL(request.url).searchParams.get("rarity") ?? "high_tier";
  const rarities = RARITIES[tier] ?? RARITIES.high_tier;
  const query = `supertype:Pokémon (${rarities.map((rarity) => `rarity:\"${rarity}\"`).join(" OR ")})`;
  const today = londonDateParts();
  try {
    const meta = await cards(new URLSearchParams({ q: query, pageSize: "1", select: "id" }), env.POKEMON_TCG_API_KEY);
    if (!meta.totalCount) throw new Error("No matching cards");
    const page = (hash(today.key) % meta.totalCount) + 1;
    const result = await cards(new URLSearchParams({ q: query, pageSize: "1", page: String(page), select: "id,name,supertype,subtypes,hp,types,rarity,artist,flavorText,images,set,cardmarket,tcgplayer,number" }), env.POKEMON_TCG_API_KEY);
    const card = result.data?.[0];
    if (!card) throw new Error("No card returned");
    return Response.json({
      title: "Pokémon Card of the Day",
      date: today.display,
      last_updated: new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date()),
      minimum_rarity: tier.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()),
      card: {
        id: card.id, name: card.name, set: card.set?.name, series: card.set?.series,
        number: card.number, rarity: card.rarity, artist: card.artist,
        flavor_text: card.flavorText, image_url: card.images?.large ?? card.images?.small,
        types: card.types ?? [], hp: card.hp,
        price: {
          cardmarket_average: card.cardmarket?.prices?.averageSellPrice ?? null,
          cardmarket_trend: card.cardmarket?.prices?.trendPrice ?? null,
          cardmarket_low: card.cardmarket?.prices?.lowPrice ?? null,
          tcgplayer_market: marketPrice(card.tcgplayer?.prices),
        },
        links: { cardmarket: card.cardmarket?.url ?? null, tcgplayer: card.tcgplayer?.url ?? null },
      },
    });
  } catch (error) {
    console.error(error);
    return Response.json({ title: "Pokémon Card of the Day", date: today.display, minimum_rarity: tier.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()), card: null, error: "No card found for today." });
  }
};
