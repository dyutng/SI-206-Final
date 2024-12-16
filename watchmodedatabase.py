import os
import urllib.request
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
import sqlite3

WATCHMODE_API = 'MdMWcFQUQg5HXno0ctOJgGQEy4SNidU1QSfiYhc4'
base_url = "https://api.watchmode.com/v1/title"
godfather_url = f"https://api.watchmode.com/v1/title/1394258/details/?apiKey={WATCHMODE_API}"

def initialize_watchmode_db():
    """
    Initialize database with a table for Watchmode.
    """
    conn = sqlite3.connect('movies.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS watchmode_table (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            release_date TEXT,
            genre TEXT,
            runtime_minutes INTEGER,
            user_rating REAL,
            critic_score INTEGER,
            us_rating TEXT
        )
    ''')

    conn.commit()
    conn.close()
    
initialize_watchmode_db()