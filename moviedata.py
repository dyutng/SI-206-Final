import os
import sqlite3
import requests
from datetime import datetime
import time
import matplotlib.pyplot as plt
from collections import defaultdict
import seaborn as sns
from tmdbv3api import TMDb, Movie, Discover

# OMDB API key
OMDB_API_KEY = 'c9ae535e'
OMDB_API_KEY = "http://www.omdbapi.com/"

# TMDB api key
TMDB_API_KEY = 'f4e6cb562855574dff73c7801d4cebbf'
tmdb = TMDb()
tmdb.api_key = TMDB_API_KEY
movie = Movie()
discover = Discover()

# sql setup
#db_name = "omdb_movies.db"
#conn = sqlite3.connect(db_name)
#cursor = conn.cursor()

def init_db():
    """
    initialize database with separate tables for omdb and tvdb
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()
    
    
    c.execute('''CREATE TABLE IF NOT EXISTS tmdb_movies
              (tmdb_id INTEGER PRIMARY KEY,
              title TEXT NOT NULL,
              release_date TEXT,
              revenue REAL,
              budget REAL,
              tmdb_rating REAL,
              tmdb_votes INTEGER,
              tmdb_popularity REAL,
              region TEXT,
              UNIQUE(tmdb_id))''')
    
    
    c.execute('''CREATE TABLE IF NOT EXISTS omdb_movies
              (id INTEGER PRIMARY KEY AUTOINCREMENT,
              movie_id INTEGER,
              title TEXT,
              year TEXT,
              genre TEXT,
              runtime INTEGER,
              box_office TEXT,
              UNIQUE(imdb_id))
              FOREIGN KEY (movie_id) REFERENCES Movies(id)''')
    
    conn.commit()
    conn.close()
