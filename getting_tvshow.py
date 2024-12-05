import requests
import json
import unittest
import os


import requests
import json

## for tvdb
API_KEY = '04e07cae-60ca-4d40-ba16-6de5031dc5e1'
BASE_URL = "https://api.thetvdb.com"

def get_auth_token(api_key):
    url = f"{BASE_URL}/login"
    payload = {"apikey": api_key}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print("Error authenticating:", response.status_code, response.text)
        return None

def get_show_details(show_name, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}/search/series"
    params = {"name": show_name}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("data", [])
    ##else:
    ##    print("Error fetching show details:", response.status_code, response.text)
    ##    return []

token = get_auth_token(API_KEY)
if token:
    show_name = "Breaking Bad"
    shows = get_show_details(show_name, token)
    for show in shows:
        print(show)
