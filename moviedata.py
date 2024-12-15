import os
import sqlite3
import requests
from datetime import datetime
import time
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
from tmdbv3api import TMDb, Movie, Discover

# OMDB API key
OMDB_API_KEY = 'c9ae535e'
OMDB_API_KEY = "http://www.omdbapi.com/"

# TMDB api key
TMDB_API_KEY = 'f4e6cb562855574dff73c7801d4cebbf'
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie = Movie()
discover = Discover()

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
    fetch movie data from omdb api
    """
    try:
        params = {
            'apikey': OMDB_API_KEY,
            't': title,
        }
        response = requests.get(OMDB_API_KEY, params=params)
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
    except Exception as e:
        print(f"Error: {e}")
    return None

def save_to_db(movie_data):
    """
    save movie data to sqlite database and take only the first genre
    """
    try:
        cursor.execute("SELECT id FROM Movies WHERE title = ?", (movie_data['title'],))
        result = cursor.fetchone()
        if result:
            return

        cursor.execute("INSERT INTO Movies (title, year) VALUES (?, ?)",
                       (movie_data['title'], movie_data['year']))
        movie_id = cursor.lastrowid

        first_genre = movie_data['genre'].split(", ")[0]  
        cursor.execute("INSERT INTO Genres (movie_id, genre, runtime) VALUES (?, ?, ?)",
                       (movie_id, first_genre, movie_data['runtime']))

        conn.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")

def get_total_movies():
    """
    check how many movies are currently in the db
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

    if total_movies < 100:
        remaining_movies = 100 - total_movies
        movies_to_fetch = min(len(movies), min(remaining_movies, 25))

        for i in range(movies_to_fetch):
            data = get_movie_data(movies[i])
            if data:
                save_to_db(data)
            time.sleep(1)

    # Plot average runtime by genre
    cursor.execute("SELECT genre, runtime FROM Genres")
    data = cursor.fetchall()

    genre_runtime = defaultdict(list)
    for genre, runtime in data:
        genre_runtime[genre].append(runtime)

    avg_runtime = {genre: sum(runtimes)/len(runtimes) for genre, runtimes in genre_runtime.items()}

    # Plot bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(avg_runtime.keys(), avg_runtime.values())
    plt.xlabel('Genre')
    plt.ylabel('Average Runtime (minutes)')
    plt.title('Average Movie Runtime vs. Movie Genre')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("runtimevsgenre_bar.png")  
    plt.show()

    # plot box plot
    plt.figure(figsize=(12, 7))
    sns.boxplot(x=[genre for genre, _ in data], y=[runtime for _, runtime in data])
    plt.xlabel('Genre')
    plt.ylabel('Runtime (minutes)')
    plt.title('Movie Runtime vs. Movie Genre')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("runtimevsgenre_box.png")  
    plt.show()

    # get year and genre data for year vs. genre comparison
    cursor.execute('''
        SELECT m.year, g.genre
        FROM Movies m
        JOIN Genres g ON m.id = g.movie_id
    ''')
    data = cursor.fetchall()

    # Group by year and genre
    year_genre_count = defaultdict(lambda: defaultdict(int))
    for year, genre in data:
        year_genre_count[year][genre] += 1

    # Prepare data for plotting
    years = sorted(year_genre_count.keys())
    genres = set(genre for year in year_genre_count.values() for genre in year)

    genre_matrix = []
    for year in years:
        genre_counts = [year_genre_count[year].get(genre, 0) for genre in genres]
        genre_matrix.append(genre_counts)

    # Plot heatmap for year vs. genre comparison
    #plt.figure(figsize=(12, 8))
    #sns.heatmap(genre_matrix, xticklabels=genres, yticklabels=years, cmap="YlGnBu", annot=True, fmt="d")
    #plt.xlabel('Genre')
    #plt.ylabel('Year')
    #plt.title('Genre Distribution by Year')
    #plt.tight_layout()
    #plt.savefig("yearvsgenre_heatmap.png")
    #plt.show()

    # Print stored Movies and Genres
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
