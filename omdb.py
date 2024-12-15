import os
import sqlite3
import requests
from datetime import datetime
import time
import json

## correlation between runtime and genre
## omdb

API_KEY = 'c9ae535e'
BASE_URL = "http://www.omdbapi.com/"

movies = ["The Matrix", "Inception", "Titanic", "The Godfather", "Interstellar"]

# SQLite setup
db_name = "OMDB.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS Movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    runtime INTEGER,
                    genre TEXT,
                    year INTEGER
                )''')
conn.commit()

def get_movie_data(title):
    """
    Fetch movie data from OMDB API.
    """
    try:
        params = {
            'apikey': API_KEY,
            't': title,
        }
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('Response') == 'True':
                runtime_str = data.get('Runtime', '0 min').split(' ')[0]  # Extract minutes
                runtime = int(runtime_str) if runtime_str.isdigit() else None
                genre = data.get('Genre', 'Unknown')
                year = int(data.get('Year', '0')) if data.get('Year', '0').isdigit() else None

                return {
                    "title": data.get('Title'),
                    "runtime": runtime,
                    "genre": genre,
                    "year": year
                }
            else:
                print(f"Movie not found: {title}")
        else:
            print(f"Error fetching data: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    return None

def save_to_db(movie_data):
    """
    Save movie data to SQLite database.
    """
    try:
        cursor.execute("INSERT INTO Movies (title, runtime, genre, year) VALUES (?, ?, ?, ?)",
                       (movie_data['title'], movie_data['runtime'], movie_data['genre'], movie_data['year']))
        conn.commit()
        print(f"Saved: {movie_data['title']}")
    except Exception as e:
        print(f"Error saving to database: {e}")

# Fetch and save data for each movie
for movie in movies:
    print(f"Fetching data for: {movie}")
    data = get_movie_data(movie)
    if data:
        save_to_db(data)
    time.sleep(1)  # To respect API rate limits

# Display results
cursor.execute("SELECT * FROM Movies")
rows = cursor.fetchall()
print("\nStored Movies:")
for row in rows:
    print(row)

# Close connection
conn.close()
