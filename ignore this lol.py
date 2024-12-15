
def get_movie_data(title):
    """
    Fetch movie data from OMDB API
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
    Save movie data to SQLite database and take only the first genre
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

def get_movies_from_tmdb(page=1):
    """
    Fetch movie titles from TMDb API (popular movies)
    """
    try:
        response = discover.discover_movies(page=page)
        movies = [movie['title'] for movie in response]
        return movies
    except Exception as e:
        print(f"Error fetching movies from TMDb: {e}")
    return []

def get_total_movies():
    """
    Check how many movies are currently in the DB
    """
    cursor.execute("SELECT COUNT(*) FROM Movies")
    return cursor.fetchone()[0]

def main():
    total_movies = get_total_movies()
    
    if total_movies < 100:
        remaining_movies = 100 - total_movies
        movies_to_fetch = min(remaining_movies, 25)  # Fetch up to 25 new movies at a time

        page = 1
        while movies_to_fetch > 0:
            movies = get_movies_from_tmdb(page)
            for movie_title in movies[:movies_to_fetch]:
                data = get_movie_data(movie_title)
                if data:
                    save_to_db(data)
                time.sleep(1)

            # Update the count of remaining movies to fetch
            movies_to_fetch -= len(movies)
            page += 1  # Move to the next page of movies

    # Generate plots
    cursor.execute("SELECT genre, runtime FROM Genres")
    data = cursor.fetchall()

    genre_runtime = defaultdict(list)
    for genre, runtime in data:
        genre_runtime[genre].append(runtime)

    avg_runtime = {genre: sum(runtimes)/len(runtimes) for genre, runtimes in genre_runtime.items()}

    plt.figure(figsize=(10, 6))
    plt.bar(avg_runtime.keys(), avg_runtime.values())
    plt.xlabel('Genre')
    plt.ylabel('Average Runtime (minutes)')
    plt.title('Average Movie Runtime vs. Movie Genre')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("runtimevsgenre_bar.png")
    plt.show()

    plt.figure(figsize=(12, 7))
    sns.boxplot(x=[genre for genre, _ in data], y=[runtime for _, runtime in data])
    plt.xlabel('Genre')
    plt.ylabel('Runtime (minutes)')
    plt.title('Movie Runtime vs. Movie Genre')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("runtimevsgenre_box.png")
    plt.show()

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
