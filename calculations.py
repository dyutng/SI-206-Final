import sqlite3

def process_data(output_file):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT AVG(user_score), AVG(critic_score)
        FROM watchmode_table
    ''')
    avg_user_score, avg_critic_score = c.fetchone()

    c.execute('''
        SELECT COUNT(*)
        FROM watchmode_table
        WHERE user_score > 70
    ''')
    high_rated_movies_count = c.fetchone()[0]

    c.execute('''
        SELECT tmdb_movies.title, tmdb_movies.release_date, omdb_movies.genre, tmdb_movies.tmdb_rating
        FROM tmdb_movies
        JOIN omdb_movies ON tmdb_movies.tmdb_id = omdb_movies.tmdb_id
    ''')
    joined_data = c.fetchall()

    with open(output_file, "a") as f:
        f.write("\n━━━━━━━━━━━━━━━━━━━\n")
        f.write(f"Movie Statistcs\n")
        f.write("━━━━━━━━━━━━━━━━━━━\n")
        f.write(f"Average User Score: {avg_user_score}\n")
        f.write(f"Average Critic Score: {avg_critic_score}\n")
        f.write(f"Movies with user score above 70: {high_rated_movies_count}\n")

    conn.close()

def movie_wrapped_report_2024(output_file):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT 
            tmdb_movies.title, 
            strftime('%Y', tmdb_movies.release_date) AS release_year,
            watchmode_table.user_score, 
            watchmode_table.critic_score,
            omdb_movies.genre
        FROM tmdb_movies
        JOIN watchmode_table ON tmdb_movies.title = watchmode_table.movie_name
        JOIN omdb_movies ON tmdb_movies.tmdb_id = omdb_movies.tmdb_id
        WHERE strftime('%Y', tmdb_movies.release_date) = '2024'
    ''')

    data = c.fetchall()

    if not data:
        print("No movies found for the year 2024.")
        return

    # init
    totalUserScore = 0
    totalCriticScore = 0
    genre_count = {}
    moviesnum = len(data)

    for row in data:
        title, release_year, user_score, critic_score, genre = row
        totalUserScore += user_score if user_score is not None else 0
        totalCriticScore += critic_score if critic_score is not None else 0

        # genres are being saved as wholes, so we take the first genre
        if genre:
            first_genre = genre.split(",")[0].strip()
            genre_count[first_genre] = genre_count.get(first_genre, 0) + 1

    avgUserScore = totalUserScore / moviesnum if moviesnum > 0 else 0
    avg_critic_score = totalCriticScore / moviesnum if moviesnum > 0 else 0

    populargenre = max(genre_count, key=genre_count.get, default="N/A")

    c.execute('''
        SELECT 
            SUM(tmdb_movies.revenue) AS total_revenue,
            SUM(tmdb_movies.budget) AS total_budget
        FROM tmdb_movies
        JOIN watchmode_table ON tmdb_movies.title = watchmode_table.movie_name
        WHERE strftime('%Y', tmdb_movies.release_date) = '2024'
    ''')

    revenue_budget = c.fetchone()
    total_revenue = revenue_budget[0] if revenue_budget[0] else 0
    total_budget = revenue_budget[1] if revenue_budget[1] else 0

    with open(output_file, "w") as f:
        f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write(f"Welcome to your 2024 Movie Wrapped! (˶ᵔ ᵕ ᵔ˶)\n")
        f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write(f"\nNumber of Movies: {moviesnum}\n")
        f.write(f"Average User Rating: {avgUserScore:.2f}\n")
        f.write(f"Average Critic Rating: {avg_critic_score:.2f}\n")
        f.write(f"Most Popular Genre: {populargenre}\n")
        f.write(f"Total Revenue: ${total_revenue:,.2f}\n")
        f.write(f"Total Budget: ${total_budget:,.2f}\n")

    conn.close()

if __name__ == "__main__":
    output_file = "final_movie_report.txt"
    movie_wrapped_report_2024(output_file)
    process_data(output_file) 
    print(f"Report generated successfully in '{output_file}'.")
