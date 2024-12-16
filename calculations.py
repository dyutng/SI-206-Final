import sqlite3

def fetch_average_tmdb_rating_per_first_genre():
    """
    Fetches the average TMDB rating per the first genre in the list of genres.
    Joins tmdb_movies and omdb_movies tables on tmdb_id and calculates the average rating.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    # join tables and calculate the average rating per first genre
    c.execute('''
        SELECT omdb_movies.genre, tmdb_movies.tmdb_rating
        FROM omdb_movies
        JOIN tmdb_movies ON omdb_movies.tmdb_id = tmdb_movies.tmdb_id
    ''')

    results = c.fetchall()
    conn.close()

    # only consider the first genre in the list
    genre_rating_map = {}

    for genre, rating in results:
        # get the first genre in the list (split by commas)
        first_genre = genre.split(',')[0]  
        
        if first_genre not in genre_rating_map:
            genre_rating_map[first_genre] = []
        
        genre_rating_map[first_genre].append(rating)

    average_rating = []
    for genre, ratings in genre_rating_map.items():
        average_rating = sum(ratings) / len(ratings)
        average_rating.append((genre, average_rating))

    return average_rating

def write_data_to_file(data):
    """
    Write the calculated data (average ratings per genre) to a text file.
    """
    with open('average_tmdb_ratings_per_genre.txt', 'w') as f:
        f.write("Genre, Average TMDB Rating\n")
        for genre, avg_rating in data:
            f.write(f"{genre}, {avg_rating:.2f}\n")
    print("Data written to 'average_tmdb_ratings_per_genre.txt'")

def main():
    # Fetch average ratings per first genre
    data = fetch_average_tmdb_rating_per_first_genre()
    
    if data:
        # Write the results to a text file
        write_data_to_file(data)
    else:
        print("No data available for processing.")

if __name__ == "__main__":
    main()
