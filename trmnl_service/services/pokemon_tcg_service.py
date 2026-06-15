import os
import random
import requests

from datetime import datetime
from zoneinfo import ZoneInfo

from .pokemon_rarities import RARITY_TIERS


class PokemonTCGService:
    CARDS_URL = "https://api.pokemontcg.io/v2/cards"
    LONDON_TZ = ZoneInfo("Europe/London")

    API_KEY = os.getenv("POKEMON_TCG_API_KEY")

    @classmethod
    def get_card_of_the_day_data(cls, minimum_rarity="high_tier"):
        now = datetime.now(cls.LONDON_TZ)
        today_key = now.strftime("%Y-%m-%d")

        rarities = RARITY_TIERS.get(
            minimum_rarity,
            RARITY_TIERS["high_tier"]
        )

        query = cls._build_query(rarities)
        card = cls._get_daily_card(query, today_key)

        if not card:
            return cls._fallback_response(now, minimum_rarity)

        return {
            "title": "Pokémon Card of the Day",
            "date": now.strftime("%d %b %Y"),
            "last_updated": now.strftime("%H:%M").lower(),
            "minimum_rarity": minimum_rarity.replace("_", " ").title(),
            "card": cls._normalize_card(card),
        }

    @classmethod
    def _get_daily_card(cls, query, today_key):
        meta = cls._fetch_cards(
            params={
                "q": query,
                "pageSize": 1,
                "select": "id",
            }
        )

        total_count = meta.get("totalCount", 0)

        if total_count == 0:
            return None

        rng = random.Random(today_key)
        selected_page = rng.randint(1, total_count)

        response = cls._fetch_cards(
            params={
                "q": query,
                "pageSize": 1,
                "page": selected_page,
                "select": (
                    "id,name,supertype,subtypes,hp,types,rarity,artist,"
                    "flavorText,images,set,cardmarket,tcgplayer,number"
                ),
            }
        )

        cards = response.get("data", [])
        return cards[0] if cards else None

    @classmethod
    def _fetch_cards(cls, params=None):
        headers = {}

        if cls.API_KEY:
            headers["X-Api-Key"] = cls.API_KEY

        try:
            response = requests.get(
                cls.CARDS_URL,
                params=params,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}

    @staticmethod
    def _build_query(rarities):
        rarity_query = " OR ".join(
            [f'rarity:"{rarity}"' for rarity in rarities]
        )

        return f'supertype:Pokémon ({rarity_query})'

    @staticmethod
    def _normalize_card(card):
        set_data = card.get("set", {})
        images = card.get("images", {})

        cardmarket = card.get("cardmarket", {})
        cardmarket_prices = cardmarket.get("prices", {})

        tcgplayer = card.get("tcgplayer", {})
        tcgplayer_prices = tcgplayer.get("prices", {})

        return {
            "id": card.get("id"),
            "name": card.get("name", "Unknown Card"),
            "set": set_data.get("name", "Unknown Set"),
            "series": set_data.get("series"),
            "number": card.get("number"),
            "rarity": card.get("rarity", "Unknown Rarity"),
            "artist": card.get("artist"),
            "flavor_text": card.get("flavorText"),
            "image_url": images.get("large") or images.get("small"),
            "types": card.get("types", []),
            "hp": card.get("hp"),
            "price": {
                "cardmarket_average": cardmarket_prices.get("averageSellPrice"),
                "cardmarket_trend": cardmarket_prices.get("trendPrice"),
                "cardmarket_low": cardmarket_prices.get("lowPrice"),
                "tcgplayer_market": PokemonTCGService._extract_tcgplayer_market_price(
                    tcgplayer_prices
                ),
            },
            "links": {
                "cardmarket": cardmarket.get("url"),
                "tcgplayer": tcgplayer.get("url"),
            },
        }

    @staticmethod
    def _extract_tcgplayer_market_price(prices):
        preferred_price_types = [
            "holofoil",
            "normal",
            "reverseHolofoil",
            "1stEditionHolofoil",
            "1stEditionNormal",
        ]

        for price_type in preferred_price_types:
            price_data = prices.get(price_type, {})
            market_price = price_data.get("market")

            if market_price is not None:
                return market_price

        return None

    @staticmethod
    def _fallback_response(now, minimum_rarity):
        return {
            "title": "Pokémon Card of the Day",
            "date": now.strftime("%d %b %Y"),
            "last_updated": now.strftime("%H:%M").lower(),
            "minimum_rarity": minimum_rarity.replace("_", " ").title(),
            "card": None,
            "error": "No card found for today.",
        }