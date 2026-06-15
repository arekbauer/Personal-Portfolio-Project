from django.urls import path
from .views import vct_ticker_view, pokemon_card_of_the_day_view

urlpatterns = [
    path('vct-ticker/', vct_ticker_view, name='trmnl_vct_ticker'),
    path(
        'pokemon-card-of-the-day/',
        pokemon_card_of_the_day_view,
        name='trmnl_pokemon_card_of_the_day'
    ),
]