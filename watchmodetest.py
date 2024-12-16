import os
import urllib.request
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
WATCHMODE_API = 'MdMWcFQUQg5HXno0ctOJgGQEy4SNidU1QSfiYhc4'
base_url = "https://api.watchmode.com/v1/title"
godfather_url = f"https://api.watchmode.com/v1/title/1394258/details/?apiKey={WATCHMODE_API}"


# Helper function to fetch and process data
def fetch_movies(movie_id):
  url = f"{base_url}/{movie_id}/details/?apiKey={WATCHMODE_API}"
  # print(f"url: {url}")
  with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    info_tuple = data["user_rating"], data["critic_score"]
    # print(f"info_tuple: {info_tuple}")
    return info_tuple

movies = {
  "The Godfather": "1394258",
  "Shawshank Redemption": "tt0111161",
  "Schindler's List": "tt0108052",
  "Raging Bull": "tt0081398",
  "Casablanca": "tt0034583",
  "Citizen Kane":"tt0033467",
  "Gone with the Wind":"tt0031381",
  "The Wizard of Oz":"tt0032138",
  "One Flew Over the Cuckoo's Nest":"tt0073486",
  "Lawrence of Arabia":"tt0056172",

}
# Store results
movie_names = []
user_scores = []
critic_scores = []

# Get scores for each movie
for movie_name, movie_id in movies.items():
  try:
    user_score, critic_score = fetch_movies(movie_id)
    movie_names.append(movie_name)
    user_scores.append(user_score * 10)  # Scale user scores to match critic scores
    critic_scores.append(critic_score)
  except Exception as e:
    print(f"Error fetching data for {movie_name}: {e}")

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))
x_positions = np.arange(len(movie_names))  # Define x positions for movies

# Plot user scores and critic scores
ax.scatter(x_positions, user_scores, color="blue", label="User Scores", zorder=3)
ax.scatter(x_positions, critic_scores, color="orange", label="Critic Scores", zorder=3)

# Connecting lines
ax.plot(x_positions, user_scores, color="blue", linestyle="--", linewidth=1, alpha=0.7)
ax.plot(x_positions, critic_scores, color="orange", linestyle="--", linewidth=1, alpha=0.7)

# Some Customization
ax.set_xticks(x_positions)
ax.set_xticklabels(movie_names, rotation=45, ha="right")
ax.set_ylabel("Scores (Out of 100)")
ax.set_title("User Scores vs Critic Scores for Selected Movies")
ax.legend()

# Adds gridlines
ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7, axis="y", zorder=0)

# Adds annotations to points
for i, (u_score, c_score) in enumerate(zip(user_scores, critic_scores)):
    ax.text(x_positions[i], u_score + 1, f"{u_score:.1f}", color="blue", fontsize=9, ha="center")
    ax.text(x_positions[i], c_score + 1, f"{c_score:.1f}", color="orange", fontsize=9, ha="center")

plt.tight_layout()
plt.show()