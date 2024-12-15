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

#test
movies = ["The Matrix", "Inception", "Titanic", "The Godfather", "Interstellar"]

# sqlite setup
db_name = "OMDB.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS Movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    runtime INTEGER,
                    year INTEGER
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Genres (
                    movie_id INTEGER,
                    genre TEXT,
                    FOREIGN KEY(movie_id) REFERENCES Movies(id)
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
                runtime_str = data.get('Runtime', '0 min').split(' ')[0]
                runtime = int(runtime_str) if runtime_str.isdigit() else None
                genres = data.get('Genre', 'Unknown').split(", ")  # Split genres into a list
                year = int(data.get('Year', '0')) if data.get('Year', '0').isdigit() else None

                return {
                    "title": data.get('Title'),
                    "runtime": runtime,
                    "genres": genres,
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
    Save movie data and genres to SQLite database.
    """
    try:
        cursor.execute("INSERT INTO Movies (title, runtime, year) VALUES (?, ?, ?)",
                       (movie_data['title'], movie_data['runtime'], movie_data['year']))
        movie_id = cursor.lastrowid  

        for genre in movie_data['genres']:
            cursor.execute("INSERT INTO Genres (movie_id, genre) VALUES (?, ?)", (movie_id, genre))
        conn.commit()
        print(f"Saved: {movie_data['title']} with genres {movie_data['genres']}")
    except Exception as e:
        print(f"Error saving to database: {e}")

for movie in movies:
    print(f"Fetching data for: {movie}")
    data = get_movie_data(movie)
    if data:
        save_to_db(data)
    time.sleep(1) 

print("\nStored Movies:")
cursor.execute("SELECT * FROM Movies")
for row in cursor.fetchall():
    print(row)

print("\nStored Genres:")
cursor.execute("SELECT * FROM Genres")
for row in cursor.fetchall():
    print(row)

conn.close()