import os
import requests
import sqlite3
import time

# API Key and Base URL
WATCHMODE_API = 'MdMWcFQUQg5HXno0ctOJgGQEy4SNidU1QSfiYhc4'
BASE_URL = "https://api.watchmode.com/v1/title/" 

def initialize_watchmode_db():
    """
    Initialize SQLite database and create a table for Watchmode data.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS watchmode_table (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            user_rating REAL,
            critic_score INTEGER,
            us_rating TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def fetch_watchmode_data(page=1):
    """
    Fetch a page of titles (max 25 per call) from Watchmode API.
    """
    url = f"{BASE_URL}345534/details/?apiKey={WATCHMODE_API}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('titles', [])
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def store_watchmode_data(titles):
    """
    Store fetched Watchmode data into the SQLite database.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    for title in titles:
        c.execute('''
            INSERT OR REPLACE INTO watchmode_table (id, title, type, user_rating, critic_score, us_rating)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            title.get('id'),
            title.get('title'),
            title.get('type'),
            title.get('user_rating', 0),
            title.get('critic_score', 0),
            title.get('us_rating', 'N/A')
        ))

    conn.commit()
    conn.close()

def fetch_and_store_watchmode_data():
    """
    Fetch data and store it in the database.
    """
    page = 1
    while True:
        titles = fetch_watchmode_data(page)
        if not titles:
            break
        
        store_watchmode_data(titles)
        page += 1
        time.sleep(1) 

# Initialize database and fetch data
initialize_watchmode_db()
fetch_and_store_watchmode_data()