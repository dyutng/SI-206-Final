import os
import sqlite3
import requests
from datetime import datetime
import time
import json

## correlation between runtime and genre
## omdb
import requests

API_KEY = '1290f5bc'
BASE_URL = "https://api.thetvdb.com/"

# Authentication request
auth_url = f"{BASE_URL}login"
headers = {
    "Content-Type": "application/json"
}
data = {
    "apikey": API_KEY
}

response = requests.post(auth_url, json=data, headers=headers)

if response.status_code == 200:
    token = response.json()['token']
    print("Authentication successful")
else:
    print("Authentication failed")
