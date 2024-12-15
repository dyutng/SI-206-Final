import os
import sqlite3
import requests
from datetime import datetime
import time
import matplotlib.pyplot as plt
from collections import defaultdict

# OMDB API Key
API_KEY = 'c9ae535e'
BASE_URL = "http://www.omdbapi.com/"

movies = ["The Matrix", "Inception", "Titanic", "The Godfather", "Interstellar"]

# sqlite setup
db_name = "movies.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS Movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    year INTEGER
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Genres (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    movie_id INTEGER,
                    genre TEXT,
                    runtime INTEGER,
                    FOREIGN KEY (movie_id) REFERENCES Movies(id)
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
    Save movie data to SQLite database, splitting genres.
    """
    try:
        cursor.execute("INSERT INTO Movies (title, year) VALUES (?, ?)",
                       (movie_data['title'], movie_data['year']))
        movie_id = cursor.lastrowid  
        
        # split genres cuz they were all put tgt into one genre if the movie had multiple
        genres = movie_data['genre'].split(", ")  
        for genre in genres:
            cursor.execute("INSERT INTO Genres (movie_id, genre, runtime) VALUES (?, ?, ?)",
                           (movie_id, genre, movie_data['runtime']))
        
        conn.commit()
        print(f"Saved: {movie_data['title']}")
    except Exception as e:
        print(f"Error saving to database: {e}")

for movie in movies:
    print(f"Fetching data for: {movie}")
    data = get_movie_data(movie)
    if data:
        save_to_db(data)
    time.sleep(1)  

cursor.execute("SELECT genre, runtime FROM Genres")
data = cursor.fetchall()

genre_runtime = defaultdict(list)
for genre, runtime in data:
    genre_runtime[genre].append(runtime)

# calculate average runtime per genre
avg_runtime = {genre: sum(runtimes)/len(runtimes) for genre, runtimes in genre_runtime.items()}

# plot
plt.figure(figsize=(10, 6))
plt.bar(avg_runtime.keys(), avg_runtime.values(), color='skyblue')
plt.xlabel('Genre')
plt.ylabel('Average Runtime (minutes)')
plt.title('Average Movie Runtime by Genre')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

print("\nStored Movies and Genres:")
cursor.execute('''
    SELECT m.title, g.genre, g.runtime 
    FROM Movies m 
    JOIN Genres g ON m.id = g.movie_id
''')
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
