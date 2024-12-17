import os
import sqlite3
import requests
import time
from tmdbv3api import TMDb, Movie, Discover
import datetime

# OMDB API key
OMDB_API_KEY = 'c9ae535e'
OMDB_URL = "http://www.omdbapi.com/"

# TMDB API key
TMDB_API_KEY = 'f4e6cb562855574dff73c7801d4cebbf'
tmdb = TMDb()  # initialize tmdb api
tmdb.api_key = TMDB_API_KEY  # set tmdb api key
movie = Movie()  # movie object for accessing tmdb movie details
discover = Discover()  # discover object for fetching popular movies

def initializedb():
    """
    Initialize database with separate tables for OMDB and TMDB.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS tmdb_movies
              (tmdb_id INTEGER PRIMARY KEY,
              title TEXT NOT NULL UNIQUE,
              release_date TEXT,
              revenue REAL,
              budget REAL,
              tmdb_rating REAL,
              tmdb_votes INTEGER,
              tmdb_popularity REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS omdb_movies
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              tmdb_id INTEGER,
              title TEXT,
              year TEXT,
              genre TEXT,
              runtime INTEGER,
              box_office TEXT,
              FOREIGN KEY (tmdb_id) REFERENCES tmdb_movies(tmdb_id),
              UNIQUE(title))''')
    
    conn.commit()
    conn.close()

def fetch_tmdb_data():
    """
    Fetch TMDB movies. Processes 25 movies at a time, stores 100+ total in database.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    total_movies = 0
    batchLimit = 25  
    page = 1

    # Check how many movies are already in the tmdb table
    c.execute("SELECT COUNT(*) FROM tmdb_movies")
    existing_movies = c.fetchone()[0]
    print(f"Currently {existing_movies} movies in the TMDB table.")

    # Loop to fetch movies until batch limit is reached
    while total_movies < batchLimit:
        try:
            # Fetch popular movies from tmdb api
            movies = discover.discover_movies({
                'sort_by': 'popularity.desc',  # Sort by popularity
                'page': page
            })

            # Loop through fetched movies
            for m in movies:
                if total_movies >= batchLimit:
                    break

                # Check if movie already exists in the database
                c.execute("SELECT 1 FROM tmdb_movies WHERE tmdb_id = ? OR title = ?", (m.id, m.title))
                if c.fetchone():
                    continue

                try:
                    details = movie.details(m.id)

                    c.execute('''
                        INSERT OR IGNORE INTO tmdb_movies 
                        (tmdb_id, title, release_date, revenue, budget, tmdb_rating, tmdb_votes, tmdb_popularity)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (details.id, details.title, details.release_date,
                         details.revenue, details.budget, 
                         details.vote_average, details.vote_count, details.popularity))

                    total_movies += 1

                except Exception as e:
                    print(f"Failed to fetch details for movie ID {m.id}: {e}")

            page += 1
            time.sleep(1)  # Avoid going over API rate limits

        except Exception as e:
            print(f"Error fetching data from TMDB API: {e}")
            break

    conn.commit()
    conn.close()
    print(f"TMDB data fetch completed. Total movies added this run: {total_movies}")

def fetch_omdb_data():
    """
    Fetch OMDB movies. Processes 25 movies at a time, stores 100+ total in database.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    total_movies = 0
    batchLimit = 25

    # Check how many movies are already in the omdb table
    c.execute("SELECT COUNT(*) FROM omdb_movies")
    existing_movies = c.fetchone()[0]
    print(f"Currently {existing_movies} movies in the OMDB table.")

    # Fetch TMDB movies that are not yet processed in OMDB table
    c.execute('''
        SELECT tmdb_id, title, release_date FROM tmdb_movies 
        WHERE tmdb_id NOT IN (SELECT tmdb_id FROM omdb_movies)
        LIMIT 25
    ''')
    movies = c.fetchall()

    for tmdb_id, title, release_date in movies:
        try:
            year = datetime.datetime.strptime(release_date, '%Y-%m-%d').year if release_date else None

            # Prepare request parameters for OMDB API
            params = {'t': title, 'y': year, 'apikey': OMDB_API_KEY}
            response = requests.get(OMDB_URL, params=params)  # Make API request
            if response.status_code == 200:  # Check for successful response
                data = response.json()  # Parse JSON response

                if data.get("Response") == "True":
                    runtime = data.get("Runtime", "0 min").split()[0]
                    box_office = data.get("BoxOffice", "N/A")
                    genre = data.get("Genre", "N/A")

                    c.execute('''
                        INSERT OR IGNORE INTO omdb_movies (tmdb_id, title, year, genre, runtime, box_office)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                              (tmdb_id, title, year, genre, int(runtime) if runtime.isdigit() else 0, 
                               box_office))
                    total_movies += 1

            # Pause to avoid exceeding API rate limits
            time.sleep(0.5)  

        except Exception as e:
            print(f"Error processing OMDB movie {title}: {e}")

    conn.commit()
    conn.close()
    print(f"OMDB fetch completed. Total movies added this run: {total_movies}")

def main():
    print("Initializing the database...")
    initializedb()
    print("Database initialized successfully.\n")

    print("Starting to fetch TMDB movie data...\n")
    fetch_tmdb_data()

    print("\nStarting to fetch OMDB movie data...\n")
    fetch_omdb_data()

    print("\nData fetching complete.")

if __name__ == "__main__":
    main()
