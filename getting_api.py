import requests

BASE_URL = "https://api.trakt.tv"

HEADERS = {
    "Content-Type": "application/json",
    "trakt-api-version": "2",
    "trakt-api-key": "34797f7c3fcf017ce15ed6615ec36ee1ad3243b9b2180957b5dbc72e9b03d2ad",
}

def get_trending_movies():
    url = f"{BASE_URL}/movies/trending"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json() 
    else:
        print("Error:", response.status_code, response.text)
        return []

movies = get_trending_movies()
for movie in movies[:5]: 
    print(movie["title"])
