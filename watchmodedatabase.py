import os
import requests
import sqlite3
import time

# API Key and Base URL
WATCHMODE_API = 'MdMWcFQUQg5HXno0ctOJgGQEy4SNidU1QSfiYhc4'
BASE_URL = "https://api.watchmode.com/v1/list-titles/"  # Adjusted endpoint for getting multiple titles

def initialize_watchmode_db():
    """
    Initialize SQLite database and create a table for Watchmode data.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    # Create table with unique constraint to avoid duplicate titles by ID
    c.execute('''
        CREATE TABLE IF NOT EXISTS watchmode_table (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            release_date TEXT,
            genre TEXT,
            runtime_minutes INTEGER,
            user_rating REAL,
            critic_score INTEGER,
            us_rating TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_watchmode_data(page=1):
    """
    Fetch a page of titles (max 25 per call) from Watchmode API.
    """
    url = f"{BASE_URL}?apiKey={WATCHMODE_API}&page={page}&limit=25"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('titles', [])
    else:
        print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
        return []

def store_watchmode_data(titles):
    """
    Store title data into the database while avoiding duplicates.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    for title in titles:
        try:
            title_id = title.get('id')
            name = title.get('title')
            media_type = title.get('type')
            release_date = title.get('release_date', '')
            genre = ", ".join(title.get('genre_names', [])) if title.get('genre_names') else ''
            runtime = title.get('runtime_minutes')
            user_rating = title.get('user_rating')
            critic_score = title.get('critic_score')
            us_rating = title.get('us_movie_rating', '')

            c.execute('''
                INSERT OR IGNORE INTO watchmode_table (id, title, type, release_date, genre, runtime_minutes, user_rating, critic_score, us_rating)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title_id, name, media_type, release_date, genre, runtime, user_rating, critic_score, us_rating))

        except Exception as e:
            print(f"Error inserting data: {e}")
    
    conn.commit()
    conn.close()

def main():
    """
    Main function to initialize database, fetch, and store data.
    """
    initialize_watchmode_db()
    page = 1 

    while True:
        print(f"Fetching page {page}...")
        titles = fetch_watchmode_data(page)

        if not titles:
            print("No more data available or error occurred.")
            break

        store_watchmode_data(titles)
        print(f"Stored {len(titles)} titles in the database.\n")
        
        time.sleep(1)
        page += 1

        conn = sqlite3.connect('movies.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM watchmode_table")
        row_count = c.fetchone()[0]
        conn.close()

        print(f"Current total rows in database: {row_count}")
        if row_count >= 100:
            print("Reached 100 rows. Exiting...")
            break

if __name__ == "__main__":
    main()
