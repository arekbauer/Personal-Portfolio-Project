from contextlib import redirect_stdout
from datetime import date
from io import StringIO
from unittest.mock import Mock, patch

import requests
from django.contrib.staticfiles import finders
from django.test import TestCase, override_settings
from django.urls import reverse

from recipes.models import Recipe

from .models import Experience, Intro, PokemonCardCache, Project, Slab, SpotifyAlbumPick
from .pokemon_tcg import refresh_card


@override_settings(SECURE_SSL_REDIRECT=False)
class HomepageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Intro.objects.create(
            description="Portfolio introduction",
            image="portfolio/images/profile.jpg",
            image_small="portfolio/images/profile-small.jpg",
        )
        Experience.objects.create(
            title="Example Company",
            subtitle="Developer",
            skills="Python, Django",
            start_date=2024,
            description="Built useful things.",
        )
        Project.objects.create(
            title="First project",
            description="An example project.",
            image="portfolio/images/project-one.jpg",
            skill1="Python",
            skill2="Django",
        )
        Project.objects.create(
            title="Second project",
            description="Another example project.",
            image="portfolio/images/project-two.jpg",
            skill1="Python",
            skill2="JavaScript",
        )
        Recipe.objects.create(
            title="Test Recipe",
            image="recipes/images/test-recipe.jpg",
        )
        PokemonCardCache.objects.create(
            card_id="base1-4",
            data={
                "id": "base1-4",
                "name": "Charizard",
                "number": "4",
                "rarity": "Rare Holo",
                "set": {"name": "Base"},
                "images": {
                    "small": "https://images.example/charizard.png",
                    "large": "https://images.example/charizard-hires.png",
                },
            },
            image_small="https://images.example/charizard.png",
            image_large="https://images.example/charizard-hires.png",
        )
        Slab.objects.create(
            card_id="base1-4",
            grader="PSA",
            grade="9",
            certification_number="12345678",
        )
        SpotifyAlbumPick.objects.create(
            spotify_album_id="album-1",
            title="Favourite Album",
            artist="Favourite Artist",
            cover_image_url="https://images.example/album.jpg",
            spotify_url="https://open.spotify.com/album/album-1",
            release_date=date(2020, 1, 1),
            data={"id": "album-1"},
        )

    def test_homepage_loads_quiet_personal_links(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Portfolio introduction")
        self.assertContains(response, "First project")
        self.assertContains(response, "A few side shelves")
        self.assertContains(response, f'href="{reverse("recipes:list")}"')
        self.assertContains(response, f'href="{reverse("albums")}"')
        self.assertContains(response, f'href="{reverse("pokemon-collection")}"')
        self.assertNotContains(response, "Test Recipe")
        self.assertNotContains(response, "Favourite Album")
        self.assertNotContains(response, "Charizard")
        self.assertNotContains(response, "Example Company")
        self.assertNotContains(response, ">Experience</a>")

    def test_project_static_assets_are_discoverable(self):
        self.assertIsNotNone(finders.find("portfolio/css/home.css"))
        self.assertIsNotNone(finders.find("portfolio/js/on-reload.js"))
        self.assertIsNotNone(finders.find("recipes/css/recipes.css"))

    def test_homepage_does_not_expose_binder_route(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, ">Binder</a>")
        self.assertNotContains(response, 'href="/binder/"')

    def test_albums_route_renders_album_picks(self):
        response = self.client.get(reverse("albums"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Favourite Album")
        self.assertContains(response, "Favourite Artist")
        self.assertContains(response, "Follow me on Spotify")
        self.assertContains(response, "https://open.spotify.com/user/n42hzpyv9obvzoyl6isvsckx0")
        self.assertContains(response, "2020")

    def test_albums_route_orders_album_picks_by_release_date_newest_first(self):
        SpotifyAlbumPick.objects.create(
            spotify_album_id="older-album",
            title="Older Album",
            artist="Older Artist",
            release_date=date(1999, 1, 1),
            data={"id": "older-album"},
        )
        SpotifyAlbumPick.objects.create(
            spotify_album_id="newer-album",
            title="Newer Album",
            artist="Newer Artist",
            release_date=date(2025, 1, 1),
            data={"id": "newer-album"},
        )

        response = self.client.get(reverse("albums"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Newer Album")
        self.assertContains(response, "Older Album")
        self.assertLess(
            response.content.decode().index("Newer Album"),
            response.content.decode().index("Favourite Album"),
        )
        self.assertLess(
            response.content.decode().index("Favourite Album"),
            response.content.decode().index("Older Album"),
        )


@override_settings(SECURE_SSL_REDIRECT=False)
class PokemonBinderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        PokemonCardCache.objects.create(
            card_id="base1-4",
            data={
                "id": "base1-4",
                "name": "Charizard",
                "number": "4",
                "rarity": "Rare Holo",
                "set": {"name": "Base"},
                "images": {
                    "small": "https://images.example/charizard.png",
                    "large": "https://images.example/charizard-hires.png",
                },
                "nationalPokedexNumbers": [6],
            },
            image_small="https://images.example/charizard.png",
            image_large="https://images.example/charizard-hires.png",
        )
        Slab.objects.create(
            card_id="base1-4",
            grader="PSA",
            grade="9",
            certification_number="12345678",
        )

    def test_binder_route_renders_slab_details(self):
        response = self.client.get(reverse("pokemon-collection"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My collection")
        self.assertContains(response, "Slabs")
        self.assertContains(response, "Charizard")
        self.assertContains(response, "PSA")
        self.assertContains(response, "12345678")

    def test_binder_static_asset_is_discoverable(self):
        self.assertIsNotNone(finders.find("portfolio/css/pokemon-binder.css"))

    @patch("portfolio.pokemon_tcg.requests.get", side_effect=requests.ConnectionError)
    def test_refresh_card_falls_back_to_stale_cache(self, _mock_get):
        cached_card = refresh_card("base1-4")

        self.assertIsNotNone(cached_card)
        self.assertEqual(cached_card.display_name, "Charizard")


@override_settings(
    SECURE_SSL_REDIRECT=False,
    SPOTIFY_CLIENT_ID="client-id",
    SPOTIFY_CLIENT_SECRET="client-secret",
    SPOTIFY_REFRESH_TOKEN="refresh-token",
)
class SpotifyApiTests(TestCase):
    @patch("portfolio.views.requests.post")
    @patch("portfolio.views.requests.get")
    def test_now_playing_returns_current_track(self, mock_get, mock_post):
        token_response = Mock()
        token_response.json.return_value = {"access_token": "token"}
        token_response.raise_for_status.return_value = None
        mock_post.return_value = token_response

        current_response = Mock(status_code=200)
        current_response.json.return_value = {
            "is_playing": True,
            "item": {
                "name": "Test Song",
                "artists": [{"name": "Test Artist"}],
                "album": {"images": [{"url": "https://example.com/cover.jpg"}]},
                "external_urls": {"spotify": "https://example.com/song"},
            },
        }
        mock_get.return_value = current_response

        response = self.client.get(reverse("now-playing"))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                "isPlaying": True,
                "title": "Test Song",
                "artist": "Test Artist",
                "albumImageUrl": "https://example.com/cover.jpg",
                "songUrl": "https://example.com/song",
            },
        )

    @patch(
        "portfolio.views.get_access_token",
        side_effect=requests.exceptions.ConnectionError,
    )
    def test_now_playing_handles_spotify_failure(self, _mock_token):
        with redirect_stdout(StringIO()):
            response = self.client.get(reverse("now-playing"))

        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(
            response.content,
            {"error": "Could not connect to Spotify."},
        )

    @patch("portfolio.views.requests.post")
    @patch("portfolio.views.requests.get")
    def test_album_page_fetches_and_caches_album_metadata(self, mock_get, mock_post):
        SpotifyAlbumPick.objects.create(spotify_album_id="album-2")
        token_response = Mock()
        token_response.json.return_value = {"access_token": "token"}
        token_response.raise_for_status.return_value = None
        mock_post.return_value = token_response

        album_response = Mock()
        album_response.json.return_value = {
            "id": "album-2",
            "name": "Fetched Album",
            "artists": [{"name": "Fetched Artist"}],
            "release_date": "2024-06-21",
            "images": [{"url": "https://images.example/fetched.jpg"}],
            "external_urls": {"spotify": "https://open.spotify.com/album/album-2"},
        }
        album_response.raise_for_status.return_value = None
        mock_get.return_value = album_response

        response = self.client.get(reverse("albums"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fetched Album")
        album = SpotifyAlbumPick.objects.get(spotify_album_id="album-2")
        self.assertEqual(album.title, "Fetched Album")
        self.assertEqual(album.artist, "Fetched Artist")
        self.assertEqual(album.release_date, date(2024, 6, 21))
