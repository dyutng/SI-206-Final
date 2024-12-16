import sqlite3

def movie_wrapped_report_2024(output_file):
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT 
            tmdb_movies.title, 
            strftime('%Y', tmdb_movies.release_date) AS release_year,
            watchmode_table.user_score, 
            watchmode_table.critic_score,
            omdb_movies.genre, 
            tmdb_movies.revenue, 
            tmdb_movies.budget,
            tmdb_movies.tmdb_rating
        FROM tmdb_movies
        JOIN watchmode_table ON tmdb_movies.title = watchmode_table.movie_name
        JOIN omdb_movies ON tmdb_movies.tmdb_id = omdb_movies.tmdb_id
        WHERE strftime('%Y', tmdb_movies.release_date) = '2024'
    ''')

    data = c.fetchall()

    #since we want to do 2024, we first need to check if there are no movies for the year 2024
    if not data:
        print("No movies found for the year 2024.")
        return

    total_user_score = total_critic_score = total_tmdb_rating = 0
    genre_count = {} #dictionary to track genre occurrences
    movies_num = len(data)

    highest_rated_movie = lowest_rated_movie = None
    highest_revenue_movie = least_revenue_movie = None
    largest_budget_movie = smallest_budget_movie = None

    #set initial values for comparison
    #float(-inf) is for max comparisons
    #guarantees any real num value (pos/neg) will replace these values on the first comparison
    max_user_score = float('-inf')
    min_user_score = float('inf')
    max_revenue = float('-inf')
    min_revenue = float('inf')
    max_budget = float('-inf')
    min_budget = float('inf')

    for row in data:
        title, release_year, user_score, critic_score, genre, revenue, budget, tmdb_rating = row
        
        #accumulate scores so i can calculate averages
        total_user_score += user_score if user_score else 0
        total_critic_score += critic_score if critic_score else 0
        total_tmdb_rating += tmdb_rating if tmdb_rating else 0

        #count the most common genre 
        if genre:
            first_genre = genre.split(",")[0].strip()
            genre_count[first_genre] = genre_count.get(first_genre, 0) + 1

        #highest and lowest user scores
        if user_score:
            if user_score > max_user_score:
                max_user_score = user_score
                highest_rated_movie = title
            if user_score < min_user_score:
                min_user_score = user_score
                lowest_rated_movie = title

        #highest and lowest revenue movies
        if revenue:
            if revenue > max_revenue:
                max_revenue = revenue
                highest_revenue_movie = title
            if revenue < min_revenue:
                min_revenue = revenue
                least_revenue_movie = title

        # largest and smallest budget movies
        if budget:
            if budget > max_budget:
                max_budget = budget
                largest_budget_movie = title
            if budget < min_budget:
                min_budget = budget
                smallest_budget_movie = title

    avg_user_score = total_user_score / movies_num if movies_num else 0
    avg_critic_score = total_critic_score / movies_num if movies_num else 0
    avg_tmdb_rating = total_tmdb_rating / movies_num if movies_num else 0

    popular_genre = max(genre_count, key = genre_count.get, default="N/A")

    #calculate total revenue and total budget for 2024 movies
    c.execute('''
        SELECT SUM(tmdb_movies.revenue), SUM(tmdb_movies.budget)
        FROM tmdb_movies
        JOIN watchmode_table ON tmdb_movies.title = watchmode_table.movie_name
        WHERE strftime('%Y', tmdb_movies.release_date) = '2024'
    ''')
    total_revenue, total_budget = c.fetchone()
    total_revenue = total_revenue if total_revenue else 0
    total_budget = total_budget if total_budget else 0

    with open(output_file, "w") as f:
        f.write("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write("Welcome to your 2024 Movie Wrapped! (˶ᵔ ᵕ ᵔ˶)")
        f.write("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        f.write(f"\nNumber of Movies: {movies_num}\n")
        f.write(f"Average User Rating: {avg_user_score:.2f}\n")
        f.write(f"Average Critic Rating: {avg_critic_score:.2f}\n")
        f.write(f"Average TMDB Rating: {avg_tmdb_rating:.2f}\n")
        f.write(f"Highest Rated Movie: {highest_rated_movie} ({max_user_score})\n")
        f.write(f"Lowest Rated Movie: {lowest_rated_movie} ({min_user_score})\n")
        f.write(f"Movie with the Highest Revenue: {highest_revenue_movie} (${max_revenue:,.2f})\n")
        f.write(f"Movie with the Least Revenue: {least_revenue_movie} (${min_revenue:,.2f})\n")
        f.write(f"Movie with the Largest Budget: {largest_budget_movie} (${max_budget:,.2f})\n")
        f.write(f"Movie with the Smallest Budget: {smallest_budget_movie} (${min_budget:,.2f})\n")
        f.write(f"Most Popular Genre: {popular_genre}\n")
        f.write(f"Total Revenue: ${total_revenue:,.2f}\n")
        f.write(f"Total Budget: ${total_budget:,.2f}\n")

    conn.close()

if __name__ == "__main__":
    output_file = "wrapped.txt"
    movie_wrapped_report_2024(output_file)
    print(f"Report generated successfully in '{output_file}'.")
