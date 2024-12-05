import requests
import sqlite3

BASE_URL = "https://api.trakt.tv"

HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": "34797f7c3fcf017ce15ed6615ec36ee1ad3243b9b2180957b5dbc72e9b03d2ad",
}

def get_trending_movies():
    url = f"{BASE_URL}/movies/trending"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json() 
    else:
        print("Error:", response.status_code, response.text)
        return []

movies = get_trending_movies()
for movie in movies[:5]: 
    print(movie["title"])

def setup_database():
    conn = sqlite3.connect("trakt_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            year INTEGER,
            overview TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            genre TEXT NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        )
    """)

    conn.commit()
    conn.close()

setup_database()

def calculate_genres_count():
    conn = sqlite3.connect("trakt_data.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT g.genre, COUNT(*) as count
        FROM genres g
        JOIN movies m ON g.movie_id = m.id
        GROUP BY g.genre
        ORDER BY count DESC
    """)

    results = cursor.fetchall()
    conn.close()
    return results

counts = calculate_genres_count()
with open("genre_counts.txt", "w") as file:
    for genre, count in counts:
        file.write(f"{genre}: {count}\n")

