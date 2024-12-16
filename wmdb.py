import urllib.request
import requests
import json
import sqlite3

WATCHMODE_API = 'MdMWcFQUQg5HXno0ctOJgGQEy4SNidU1QSfiYhc4'
base_url = "https://api.watchmode.com/v1/title"
list_titles_url = "https://api.watchmode.com/v1/list-titles/?apiKey=" + WATCHMODE_API

def initialize_database():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
              id INTEGER PRIMARY KEY,
              type TEXT NOT NULL, 
              movie_name TEXT NOT NULL,
              user_score REAL,
              critic_score REAL
        )
    ''')
    conn.commit()
    conn.close()

def fetch_movies(movie_id):
    url = f"{base_url}/{movie_id}/details/?apiKey={WATCHMODE_API}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        user_rating = data.get("user_rating", 0) 
        critic_score = data.get("critic_score", 0)  
        return user_rating, critic_score

def store_movie_data(movie_name, movie_type, user_score, critic_score):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO movies (movie_name, type, user_score, critic_score)
        VALUES (?, ?, ?, ?)
    ''', (movie_name, movie_type, user_score, critic_score))
    conn.commit()
    conn.close()

def get_movie_list(page=1, limit=25):
    try:
        url = f"{list_titles_url}&page={page}&limit={limit}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            titles = data.get('titles', [])
            movie_list = [(title['title'], title['id'], title['type']) for title in titles]
            return movie_list
        else:
            print(f"Error fetching movie list: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching movie list: {e}")
        return []

def get_movie_data():
    movie_names = []
    user_scores = []
    critic_scores = []
    
    page = 1
    batch_size = 25
    while True:
        print(f"Fetching page {page}...")
        movie_list = get_movie_list(page=page, limit=batch_size)

        if not movie_list:
            print("No more movies found or error occurred.")
            break

        for movie_name, movie_id, movie_type in movie_list:
            if movie_type != 'movie':
                continue

            try:
                user_score, critic_score = fetch_movies(movie_id)
                movie_names.append(movie_name)
                user_scores.append(user_score * 10)  
                critic_scores.append(critic_score)

                store_movie_data(movie_name, movie_type, user_score * 10, critic_score)
            except Exception as e:
                print(f"Error fetching data for {movie_name}: {e}")

        page += 1 
    
    return movie_names, user_scores, critic_scores

def main():
    initialize_database()

    movie_names, user_scores, critic_scores = get_movie_data()

if __name__ == "__main__":
    main()
