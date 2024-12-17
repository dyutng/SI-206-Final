import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.ticker as ticker

def fetch_data():
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    #join omdb_movies and tmdb_movies tables and fetch relevant data
    c.execute('''
              SELECT omdb_movies.genre, omdb_movies.runtime, omdb_movies.box_office, 
              tmdb_movies.tmdb_rating, tmdb_movies.budget, tmdb_movies.revenue, 
              omdb_movies.year
        FROM omdb_movies
        JOIN tmdb_movies ON omdb_movies.tmdb_id = tmdb_movies.tmdb_id
    ''')
    data = c.fetchall()
    conn.close()

    #pandas dataframe
    df = pd.DataFrame(data, columns = ['genre', 'runtime', 'box_office', 
                                       'tmdb_rating', 'budget', 'revenue', 'year'])

    #genres are being stores as multiple genres
    #ex: an action and sci-fi movie would be "Action, Sci-Fi"
    #take only the first genre if multiple genres are present
    df['genre'] = df['genre'].apply(lambda x: x.split(',')[0] if pd.notnull(x) else 'Unknown')

    df['year'] = pd.to_numeric(df['year'], errors = 'coerce')
    df['runtime'] = pd.to_numeric(df['runtime'], errors = 'coerce')
    df['budget'] = pd.to_numeric(df['budget'], errors = 'coerce')
    df['revenue'] = pd.to_numeric(df['revenue'], errors = 'coerce')

    return df

def plot_runtime_vs_genre(df):
    """
    Plot the average movie runtime for each genre (bar plot).
    """
    #get rid of rows with invalid runtime
    filterdf = df[df['runtime'] > 0]

    #group by genre, calculate the average runtime
    genre_runtime = filterdf.groupby('genre')['runtime'].mean().dropna().sort_values(ascending = False)

    plt.figure(figsize = (12, 6))
    sns.barplot(x = genre_runtime.index, y = genre_runtime.values, color='skyblue')

    plt.xticks(rotation=45)
    plt.title('Average Movie Runtime by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Average Runtime (minutes)')
    plt.tight_layout()  
    plt.savefig("runtime_vs_genre.png")
    plt.show()

def plot_ratings_vs_genre_bar(df):
    """
    Plot the average TMDB ratings for each genre (bar plot).
    """
    #group by genre, calculate the average tmdb rating
    genre_ratings = df.groupby('genre')['tmdb_rating'].mean().dropna().sort_values(ascending = False)

    plt.figure(figsize = (12, 6))
    sns.barplot(x = genre_ratings.index, y = genre_ratings.values, color='#FF5733')

    plt.xticks(rotation = 45)
    plt.title('Average TMDB Ratings by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Average TMDB Rating (Out of 10)')
    plt.tight_layout()
    plt.savefig("rating_vs_genre_bar.png")
    plt.show()

def plot_rating_vs_genre_box(df):
    """
    Plot the distribution of TMDB ratings by genre (box plot).
    """
    #get rid of rows with invalid ratings
    df = df[df['tmdb_rating'] > 0]

    plt.figure(figsize = (12, 6))
    sns.boxplot(x = 'genre', y = 'tmdb_rating', data = df, color='lightgreen')

    plt.title('Distribution of TMDB Ratings by Genre')
    plt.xlabel('Genre')
    plt.ylabel('TMDB Rating (Out of 10)')
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.savefig("rating_vs_genre.png")
    plt.show()

def plot_revenue_vs_rating(df):
    """
    Scatter plot of revenue vs. TMDB Ratings with line of best fit.
    """
    #clean and convert revenue column to numeric type
    df['revenue'] = pd.to_numeric(df['revenue'].
                                  replace('N/A', '0').replace('$', '').replace(',', ''), errors='coerce')
    
    #get rid of rows with invalid revenue and ratings
    df = df[(df['revenue'] > 0) & (df['tmdb_rating'] > 0)]

    plt.figure(figsize = (12, 7))

    sns.regplot(data = df, x = 'tmdb_rating', y = 'revenue', 
                scatter_kws = {'alpha':0.5}, line_kws = {'color':'red'})

    plt.title('Revenue vs TMDB Ratings')
    plt.xlabel('TMDB Rating (Out of 10)')
    plt.ylabel('Revenue (in Millions)')
    plt.tight_layout()
    plt.savefig("revenue_vs_rating_with_fit.png")
    plt.show()


def plot_avg_revenue_vs_genre_box(df):
    """
    Box plot of revenue vs. genre.
    """
    #clean and convert the revenue column to numeric type
    df['revenue'] = pd.to_numeric(df['revenue'].
                                  replace('N/A', '0').replace('$', '').replace(',', ''), errors='coerce')
    
    #filter out rows with invalid revenue
    df = df[df['revenue'] > 0]

    plt.figure(figsize = (12, 6))
    sns.boxplot(data = df, x = 'genre', y = 'revenue', color='#FFCC99')

    plt.title('Revenue by Genre')
    plt.xlabel('Genre')
    plt.ylabel('Revenue (in Millions)')
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.savefig("revenue_vs_genre_box.png")
    plt.show()


def main():
    df = fetch_data()

    plot_runtime_vs_genre(df)
    plot_ratings_vs_genre_bar(df)
    plot_revenue_vs_rating(df)
    plot_avg_revenue_vs_genre_box(df)
    plot_rating_vs_genre_box(df)

if __name__ == "__main__":
    main()
