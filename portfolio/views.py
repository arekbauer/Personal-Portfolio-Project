import requests
import base64
from django.shortcuts import render
from collections import Counter
from .models import Project
from .models import Intro
from .models import Experience
from django.conf import settings
from django.http import JsonResponse

# Spotify API Endpoints
TOKEN_ENDPOINT = 'https://accounts.spotify.com/api/token'
NOW_PLAYING_ENDPOINT = 'https://api.spotify.com/v1/me/player/currently-playing'
RECENTLY_PLAYED_ENDPOINT = 'https://api.spotify.com/v1/me/player/recently-played'

def home(request):
    projects = Project.objects.all()
    intros = Intro.objects.all()
    experiences = Experience.objects.all()
    
    all_skills = []
    muted_skills = ["C#", "A* Pathfinding"]
    
    for project in projects:
        skills = [project.skill1, project.skill2, project.skill3, project.skill4]
        filtered_skills = [skill for skill in skills if skill and skill not in muted_skills] #filtering out None or empty values
        # Add the filtered skills to the all_skills list
        
        all_skills.extend(filtered_skills)
    
    # Use Counter to count occurrences of each skill
    skill_counts = Counter(all_skills)
    
    # Get the 4 most common skills
    most_common_skills = [skill for skill, _ in skill_counts.most_common(4)]
    
    return render(request, 'portfolio/home.html', {
        'projects': projects,              
        'intros': intros,                  
        'experiences': experiences,            
        'most_common_skills': most_common_skills,  
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

