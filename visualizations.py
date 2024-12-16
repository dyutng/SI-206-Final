import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

def fetch_data():
    """
    Fetches box_office and TMDB_ratings data from the database.
    Some movies (like Wicked) are new so their box office value is "N/A" - skip those.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        SELECT omdb_movies.box_office, tmdb_movies.tmdb_rating
        FROM omdb_movies
        JOIN tmdb_movies ON omdb_movies.tmdb_id = tmdb_movies.tmdb_id
        WHERE omdb_movies.box_office != "N/A" AND tmdb_movies.tmdb_rating IS NOT NULL
    ''')

    data = c.fetchall()
    conn.close()

    box_office = []
    tmdb_rating = []

    for row in data:
        box_office_value = row[0].replace(",", "").replace("$", "")
        if box_office_value.isdigit():  
            box_office.append(float(box_office_value))
            tmdb_rating.append(row[1])

    return box_office, tmdb_rating

def plot_data(box_office, tmdb_rating):
    """
    plot a scatter plot of box office vs TMDB rating.
    """
    plt.figure(figsize=(10, 6))
    sns.set(style="whitegrid")

    plt.scatter(box_office, tmdb_rating, color='blue', alpha=0.7)
    plt.title('Box Office vs TMDB Rating', fontsize=16)
    plt.xlabel('Box Office (in USD)', fontsize=14)
    plt.ylabel('TMDB Rating', fontsize=14)

    # regression line
    sns.regplot(x=box_office, y=tmdb_rating, scatter=False, color='red')

    plt.show()

def main():
    box_office, tmdb_rating = fetch_data()
    if box_office and tmdb_rating:
        plot_data(box_office, tmdb_rating)
    else:
        print("No valid data to plot.")

if __name__ == "__main__":
    main()
