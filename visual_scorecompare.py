import matplotlib.pyplot as plt
import numpy as np
import sqlite3

def get_common_movies():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT tmdb_movies.tmdb_id, tmdb_movies.title, tmdb_movies.tmdb_rating, 
               watchmode_table.user_score, watchmode_table.critic_score
        FROM tmdb_movies
        INNER JOIN omdb_movies ON tmdb_movies.tmdb_id = omdb_movies.tmdb_id
        INNER JOIN watchmode_table ON omdb_movies.title = watchmode_table.movie_name
    ''')

    common_movies = c.fetchall()
    conn.close()
    
    return common_movies

def plot_scores():
    common_movies = get_common_movies()
    
    tmdb_ratings = []
    user_scores = []
    critic_scores = []
    movie_titles = []
    
    for movie in common_movies:
        tmdb_ratings.append(movie[2])  # tmdb rating is out of 10
        user_scores.append(movie[3] / 10)  # watchmode user score to out of 10
        critic_scores.append(movie[4] / 10)  # watchmode critic score to out of 10
        movie_titles.append(movie[1])

    x = np.arange(len(movie_titles))
    
    plt.figure(figsize=(10, 6))
    plt.plot(x, tmdb_ratings, label='TMDB Rating', color='blue', marker='o')
    plt.plot(x, user_scores, label='Watchmode User Score', color='red', marker='o')
    plt.plot(x, critic_scores, label='Watchmode Critic Score', color='orange', marker='o')
    
    plt.xlabel('Movies')
    plt.ylabel('Ratings (Out of 10)')
    plt.title('Movie Ratings: TMDB vs Watchmode')
    plt.xticks(x, movie_titles, rotation=90)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig("ratings_tmdbvswatchmode.png")
    plt.show()

def main():
    plot_scores()

if __name__ == "__main__":
    main()
