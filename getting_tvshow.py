import requests
import json
import unittest
import os
import sqlite3

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

def setup_database():
    conn = sqlite3.connect("tvdb_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shows (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            runtime INTEGER,
            overview TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            show_id INTEGER NOT NULL,
            genre TEXT NOT NULL,
            FOREIGN KEY (show_id) REFERENCES shows (id)
        )
    """)

    conn.commit()
    conn.close()

setup_database()

def save_show_to_db(show, genres):
    conn = sqlite3.connect("tvdb_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO shows (id, name, runtime, overview)
        VALUES (?, ?, ?, ?)
    """, (show["id"], show["seriesName"], show.get("runtime"), show.get("overview")))

    for genre in genres:
        cursor.execute("""
            INSERT INTO genres (show_id, genre)
            VALUES (?, ?)
        """, (show["id"], genre))

    conn.commit()
    conn.close()

#for show in shows:
#    genres = show.get("genre", [])
#    save_show_to_db(show, genres)

def save_show_to_db(show, genres):
    conn = sqlite3.connect("tvdb_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO shows (id, name, runtime, overview)
        VALUES (?, ?, ?, ?)
    """, (show["id"], show["seriesName"], show.get("runtime"), show.get("overview")))

    for genre in genres:
        cursor.execute("""
            INSERT INTO genres (show_id, genre)
            VALUES (?, ?)
        """, (show["id"], genre))

    conn.commit()
    conn.close()

def get_genre_length_data():
    conn = sqlite3.connect("tvdb_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT g.genre, AVG(s.runtime) as avg_runtime
        FROM genres g
        JOIN shows s ON g.show_id = s.id
        GROUP BY g.genre
        ORDER BY avg_runtime DESC
    """)

    results = cursor.fetchall()
    conn.close()
    return results

