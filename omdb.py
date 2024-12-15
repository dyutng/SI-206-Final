import os
import sqlite3
import requests
from datetime import datetime
import time
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns

# OMDB API key
API_KEY = 'c9ae535e'
BASE_URL = "http://www.omdbapi.com/"

# sql setup
db_name = "omdb_movies.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS Movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT UNIQUE,
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
        cursor.execute("SELECT id FROM Movies WHERE title = ?", (movie_data['title'],))
        result = cursor.fetchone()
        if result:
            print(f"Movie '{movie_data['title']}' already exists in the database. Skipping.")
            return

        cursor.execute("INSERT INTO Movies (title, year) VALUES (?, ?)",
                       (movie_data['title'], movie_data['year']))
        movie_id = cursor.lastrowid

        # split genres cuz they were all put tgt into one genre if the movie had multiple
        genres = movie_data['genre'].split(", ") 
        for genre in genres:
            cursor.execute("INSERT INTO Genres (movie_id, genre, runtime) VALUES (?, ?, ?)",
                           (movie_id, genre, movie_data['runtime']))

        conn.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")

def get_total_movies():
    """
    Check how many movies are currently in the database.
    """
    cursor.execute("SELECT COUNT(*) FROM Movies")
    return cursor.fetchone()[0]

def main():
    movies = [
        "The Matrix", "Inception", "Titanic", "The Godfather", "Interstellar",
        "Avatar", "Pulp Fiction", "The Dark Knight", "Forrest Gump", "Fight Club",
        "Goodfellas", "The Shawshank Redemption", "Gladiator", "The Lion King", 
        "The Silence of the Lambs", "Saving Private Ryan", "Jurassic Park", 
        "The Green Mile", "Schindler's List", "The Departed", "Braveheart",
        "Casablanca", "A Beautiful Mind", "La La Land", "The Prestige", "Whiplash",
        "Memento", "Up", "Coco", "Toy Story", "Wall-E", "Ratatouille"
    ]
    
    total_movies = get_total_movies()
    print(f"total movies in database: {total_movies}")

    # limit data stored to 25 
    if total_movies < 100:
        remaining_movies = 100 - total_movies
        movies_to_fetch = min(len(movies), min(remaining_movies, 25))

        for i in range(movies_to_fetch):
            data = get_movie_data(movies[i])
            if data:
                save_to_db(data)
            time.sleep(1)  

        print(f"added {movies_to_fetch} movies to the database")
    else:
        print("db already has 100 or more movies.")

    # plot average runtime by genre
    cursor.execute("SELECT genre, runtime FROM Genres")
    data = cursor.fetchall()

    genre_runtime = defaultdict(list)
    for genre, runtime in data:
        genre_runtime[genre].append(runtime)

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

if __name__ == "__main__":
    main()
    conn.close()
