import requests
from django.conf import settings

from .models import PokemonCardCache


CARD_ENDPOINT = "https://api.pokemontcg.io/v2/cards/{card_id}"
CARD_FIELDS = "id,name,set,number,rarity,images,nationalPokedexNumbers"


def get_cached_card(card_id):
    cache = PokemonCardCache.objects.filter(card_id=card_id).first()
    if cache and cache.data:
        return cache

    return refresh_card(card_id)


def refresh_card(card_id):
    cache = PokemonCardCache.objects.filter(card_id=card_id).first()
    headers = {}
    api_key = getattr(settings, "POKEMON_TCG_API_KEY", "")
    if api_key:
        headers["X-Api-Key"] = api_key

    try:
        response = requests.get(
            CARD_ENDPOINT.format(card_id=card_id),
            params={"select": CARD_FIELDS},
            headers=headers,
            timeout=8,
        )
        response.raise_for_status()
        card_data = response.json()["data"]
    except (KeyError, requests.RequestException):
        if cache:
            return cache
        return None

    images = card_data.get("images", {})
    cache, _created = PokemonCardCache.objects.update_or_create(
        card_id=card_id,
        defaults={
            "data": card_data,
            "image_small": images.get("small", ""),
            "image_large": images.get("large", ""),
        },
    )
    return cache


def attach_card_cache(items):
    item_list = list(items)
    caches = {}

    for item in item_list:
        card_id = item.card_id
        if card_id not in caches:
            caches[card_id] = get_cached_card(card_id)
        item.card = caches[card_id]

    return item_list
