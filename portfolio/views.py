import requests
import base64
from datetime import date
from django.shortcuts import render
from .models import Project
from .models import Intro
from django.conf import settings
from django.http import JsonResponse
from .models import Slab, SpotifyAlbumPick
from .pokemon_tcg import attach_card_cache

# Spotify API Endpoints
TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'
NOW_PLAYING_ENDPOINT = 'https://api.spotify.com/v1/me/player/currently-playing'
RECENTLY_PLAYED_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played'
ALBUM_ENDPOINT = 'https://api.spotify.com/v1/albums/{album_id}'

def home(request):
    projects = Project.objects.all()
    intros = Intro.objects.all()
    
    return render(request, 'portfolio/home.html', {
        'projects': projects,              
        'intros': intros,                  
    })


def pokemon_slabs(request):
    slabs = attach_card_cache(Slab.objects.filter(featured=True))

    return render(request, 'portfolio/pokemon-slabs.html', {
        'slabs': slabs,
    })


def albums(request):
    album_picks = attach_album_metadata(SpotifyAlbumPick.objects.filter(featured=True))

    return render(request, 'portfolio/albums.html', {
        'album_picks': album_picks,
    })
    
def get_access_token():
    """Gets a new access token from Spotify using the refresh token."""
    client_id = settings.SPOTIFY_CLIENT_ID
    client_secret = settings.SPOTIFY_CLIENT_SECRET
    refresh_token = settings.SPOTIFY_REFRESH_TOKEN

    auth_str = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    headers = {
        'Authorization': f'Basic {auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = requests.post(TOKEN_ENDPOINT, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()['access_token']

def get_now_playing(request):
    """Fetches the currently playing song, or the last played song as a fallback."""
    try:
        access_token = get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        
        # 1. First, check for a currently playing song
        response = requests.get(NOW_PLAYING_ENDPOINT, headers=headers)

        if response.status_code == 200:
            song = response.json()
            if song and song.get('is_playing'):
                data = {
                    'isPlaying': True,
                    'title': song['item']['name'],
                    'artist': ', '.join([artist['name'] for artist in song['item']['artists']]),
                    'albumImageUrl': song['item']['album']['images'][0]['url'],
                    'songUrl': song['item']['external_urls']['spotify'],
                }
                return JsonResponse(data)

        # 2. If nothing is playing, get the most recently played track
        response = requests.get(f"{RECENTLY_PLAYED_ENDPOINT}?limit=1", headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data.get('items'):
            return JsonResponse({'isPlaying': False})

        last_played_song = data['items'][0]['track']
        fallback_data = {
            'isPlaying': False,
            'title': last_played_song['name'],
            'artist': ', '.join([artist['name'] for artist in last_played_song['artists']]),
            'albumImageUrl': last_played_song['album']['images'][0]['url'],
            'songUrl': last_played_song['external_urls']['spotify'],
        }
        return JsonResponse(fallback_data)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return JsonResponse({'error': 'Could not connect to Spotify.'}, status=500)


def attach_album_metadata(album_picks):
    picks = list(album_picks)

    for pick in picks:
        if not pick.data:
            refresh_album_metadata(pick)

    return sorted(
        picks,
        key=lambda pick: (pick.release_date is not None, pick.release_date or date.min),
        reverse=True,
    )


def refresh_album_metadata(album_pick):
    try:
        access_token = get_access_token()
        response = requests.get(
            ALBUM_ENDPOINT.format(album_id=album_pick.spotify_album_id),
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=8,
        )
        response.raise_for_status()
        album_data = response.json()
    except requests.exceptions.RequestException:
        return album_pick

    artists = ", ".join(artist["name"] for artist in album_data.get("artists", []))
    images = album_data.get("images", [])
    cover_image_url = images[0]["url"] if images else ""
    spotify_url = album_data.get("external_urls", {}).get("spotify", "")
    release_date = parse_spotify_release_date(album_data.get("release_date", ""))

    album_pick.title = album_data.get("name", "")
    album_pick.artist = artists
    album_pick.cover_image_url = cover_image_url
    album_pick.spotify_url = spotify_url
    album_pick.release_date = release_date
    album_pick.data = album_data
    album_pick.save(update_fields=[
        "title",
        "artist",
        "cover_image_url",
        "spotify_url",
        "release_date",
        "data",
        "fetched_at",
    ])
    return album_pick


def parse_spotify_release_date(value):
    parts = value.split("-")

    try:
        year = int(parts[0])
        month = int(parts[1]) if len(parts) > 1 else 1
        day = int(parts[2]) if len(parts) > 2 else 1
    except (IndexError, TypeError, ValueError):
        return None

    try:
        return date(year, month, day)
    except ValueError:
        return None

