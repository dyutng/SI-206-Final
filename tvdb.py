import os
import sqlite3
import requests
from datetime import datetime
import time
import json

## correlation between runtime and genre
## for tvdb

API_KEY = '9ec49918-212d-4918-9e05-da99e17ad799'
BASE_URL = "https://www.thetvdb.com/"
LOGIN_URL = f"{BASE_URL}/login"

headers = {
    'Content-Type': 'application/json'
}

data = {
    'apikey': API_KEY
}

response = requests.post(LOGIN_URL, json=data, headers=headers)

if response.status_code == 200:
    token = response.json()['token']
    print(f"Authenticated successfully! Token: {token}")
else:
    print(f"Failed to authenticate: {response.status_code}")

    SHOW_ID = "ID371028" 
SHOW_URL = f"{BASE_URL}/series/{SHOW_ID}"

headers['Authorization'] = f"Bearer {token}"

response = requests.get(SHOW_URL, headers=headers)

if response.status_code == 200:
    show_data = response.json()
    
    # Extract show details
    show_name = show_data['data']['seriesName']
    number_of_seasons = show_data['data']['numberOfSeasons']
    genre = show_data['data']['genre']
    
    print(f"Show Name: {show_name}")
    print(f"Number of Seasons: {number_of_seasons}")
    print(f"Genre: {genre}")
    
    # Fetch episodes details
    episodes = []
    for season in range(1, number_of_seasons + 1):
        season_url = f"{BASE_URL}/series/{SHOW_ID}/episodes/query?airedSeason={season}"
        season_response = requests.get(season_url, headers=headers)
        
        if season_response.status_code == 200:
            season_data = season_response.json()
            episodes_in_season = len(season_data['data'])
            episodes.append(episodes_in_season)
    
    # Total episodes
    total_episodes = sum(episodes)
    print(f"Total Episodes: {total_episodes}")
    for season, count in enumerate(episodes, start=1):
        print(f"Season {season}: {count} episodes")
else:
    print(f"Failed to fetch show details: {response.status_code}")

