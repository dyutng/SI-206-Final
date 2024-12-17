import urllib.request
import requests
import json
import sqlite3

WATCHMODE_API = 'WY5zoIJY8YJxP9VKwReDGFOYBwZtQxrelOnouu2e'

# Spare API Key (for grading session):
# RrqdEqYeGIltkfmnW8BA1cDu3c5xyiYIldfZnKhN

# Spare API Key (for submission, instructor's grading):
# bnIgnohrXlQ8tEvO7kzqjguo2RUqSYGg72N0QPYR

#theres a limit of 1000 per api key
#if it says too many requests or something like that you need to change your api key

baseURL = "https://api.watchmode.com/v1/title"
listTitleURL = "https://api.watchmode.com/v1/list-titles/?apiKey=" + WATCHMODE_API


def initialize_database(): #making watchmode_table
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS watchmode_table ( 
              id INTEGER PRIMARY KEY,
              movie_name TEXT NOT NULL UNIQUE,
              type TEXT NOT NULL, 
              user_score REAL,
              critic_score REAL
        )
    ''')
    conn.commit()
    conn.close()

def fetch_movies(movie_id):
    url = f"{baseURL}/{movie_id}/details/?apiKey={WATCHMODE_API}"
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        user_rating = data.get("user_rating", 0) 
        critic_score = data.get("critic_score", 0)  
        return user_rating, critic_score

#store info (name, type, user score, critic score in the db
# ignore if theres duplicates
def store_movie_data(movie_name, movie_type, user_score, critic_score):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('''
        INSERT OR IGNORE INTO watchmode_table (movie_name, type, user_score, critic_score)
        VALUES (?, ?, ?, ?)
    ''', (movie_name, movie_type, user_score, critic_score))
    conn.commit()
    conn.close()


#getz a list of movies with title, id, and type from the watchmode api.
# processes movies page by page, limit of 25 movies
def get_movie_list(page = 1, limit = 25):
    try:
        url = f"{listTitleURL}&page={page}&limit={limit}" #api request url
        response = requests.get(url)  #get request to watchmode api
        if response.status_code == 200: #check if request was successful
            data = response.json() #parse json response
            titles = data.get('titles', [])
            movie_list = [(title['title'], title['id'], title['type']) for title in titles]
            return movie_list
        else:
            print(f"Error fetching movie list: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching movie list: {e}")
        return []

def get_movie_data(starting_page = 1):

    movie_names = []
    user_scores = []
    critic_scores = []
    
    page = starting_page
    batch_size = 25
    stored_movie_count = 0  
    max_movies = 25  
    processed_movie_ids = set() 

    #check the current number of movies in the database
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM watchmode_table')
    current_count = c.fetchone()[0]
    conn.close()

    print(f"Currently {current_count} movies in the database.")

    while stored_movie_count < max_movies:
        movie_list = get_movie_list(page = page, limit = batch_size)

        if not movie_list:
            print("No more movies found or error occurred.")
            break

        for movie_name, movie_id, movie_type in movie_list:
            if movie_type != 'movie':  #skip non-movies (in movie_type)
                continue

            if movie_id in processed_movie_ids: #skip already movie ids that are alr processed
                continue

            try:
                user_score, critic_score = fetch_movies(movie_id)
                if user_score == 0 and critic_score == 0: #skip movies with no scores
                    continue 

                #check if the movie already exists in the database
                conn = sqlite3.connect('movies.db')
                c = conn.cursor()
                c.execute('SELECT COUNT(*) FROM watchmode_table WHERE movie_name = ?', 
                          (movie_name,))
                count = c.fetchone()[0]
                conn.close()

                if count == 0:
                    store_movie_data(movie_name, movie_type, user_score * 10, critic_score)
                    stored_movie_count += 1
                    movie_names.append(movie_name)
                    user_scores.append(user_score * 10)
                    critic_scores.append(critic_score)

                    processed_movie_ids.add(movie_id) #mark movie id as processed
                    if stored_movie_count >= max_movies:
                        break

            except Exception as e:
                print(f"Error fetching data for {movie_name}: {e}")

        page += 1  
    
    print(f"\nMovie data fetch completed. Total movies added this run: {stored_movie_count}")
    return movie_names, user_scores, critic_scores

def main():
    print("Initializing the database...")
    initialize_database()
    print("Database initialized successfully.\n")

    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM watchmode_table')
    current_count = c.fetchone()[0]
    conn.close()

    starting_page = (current_count // 25) + 1 

    #calculate starting page based on existing movies  
    movie_names, user_scores, critic_scores = get_movie_data(starting_page = starting_page) 

    print("Fetching complete.")

if __name__ == "__main__":
    main()
