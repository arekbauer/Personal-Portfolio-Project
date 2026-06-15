from django.http import JsonResponse
from .services import VLRService, PokemonTCGService

def vct_ticker_view(request):
    """
    Endpoint for the TRMNL device to poll.
    """
    data = VLRService.get_vct_dashboard_data()
    
    status_code = 200 if "error" not in data else 502
    return JsonResponse(data, status=status_code)

def pokemon_card_of_the_day_view(request):
    rarity = request.GET.get("rarity", "high_tier")

    data = PokemonTCGService.get_card_of_the_day_data(
        minimum_rarity=rarity
    )

    return JsonResponse(data)