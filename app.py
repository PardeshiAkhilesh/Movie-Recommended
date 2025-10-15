from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests
from functools import lru_cache
from datetime import datetime

app = Flask(__name__)

# Load movie data and similarity matrix
movies_list = pickle.load(open('Data/movies.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('Data/similarity.pkl', 'rb'))

# OMDb configuration and defaults
OMDB_API_KEY = 'e0585436'
DEFAULT_POSTER_URL = "https://via.placeholder.com/300x450.png?text=No+Poster"


@lru_cache(maxsize=512)
def fetch_movie_details(movie_title):
    """Fetch detailed metadata for a movie using the OMDb API."""
    normalized_title = (movie_title or "").strip()
    if not normalized_title:
        return None

    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={requests.utils.quote(normalized_title)}"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') != 'True':
            return None

        poster_url = data.get('Poster')
        if not poster_url or poster_url == 'N/A':
            poster_url = DEFAULT_POSTER_URL

        plot = data.get('Plot')
        if not plot or plot == 'N/A':
            plot = "Plot details are currently unavailable."

        return {
            "title": data.get('Title', normalized_title),
            "poster": poster_url,
            "plot": plot,
            "genre": data.get('Genre', 'Unknown'),
            "released": data.get('Released', 'Unknown'),
            "runtime": data.get('Runtime', 'Unknown'),
            "director": data.get('Director', 'Unknown'),
            "actors": data.get('Actors', 'Unknown'),
            "language": data.get('Language', 'Unknown'),
            "imdb_rating": data.get('imdbRating', 'N/A'),
            "year": data.get('Year', 'N/A'),
        }
    except Exception as exc:
        print(f"❌ Error fetching details for {movie_title}: {exc}")
        return None


def fetch_poster(movie_title):
    """Return a poster image URL for the given movie title."""
    details = fetch_movie_details(movie_title)
    if details:
        return details["poster"]
    return DEFAULT_POSTER_URL


def get_recommend(movie_name):
    """Return a list of recommended movies with poster URLs."""
    try:
        movie_index = movies[movies["title"] == movie_name].index[0]
    except IndexError:
        return []

    distances = similarity[movie_index]
    top_movies = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:10]

    recommended_movies = []
    recommended_posters = []

    for i in top_movies:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))

    return list(zip(recommended_movies, recommended_posters))


@app.route('/')
def home():
    return render_template(
        'index.html',
        movie_list=movies['title'].tolist(),
        recommendations=None,
        selected_movie=None,
        search_query=None,
        error_message=None,
        current_year=datetime.utcnow().year
    )


@app.route('/recommend', methods=['POST'])
def recommend():
    movie_name = (request.form.get('movie') or "").strip()

    if not movie_name:
        return render_template(
            'index.html',
            movie_list=movies['title'].tolist(),
            recommendations=None,
            selected_movie=None,
            search_query=None,
            error_message="Please enter a movie title to get recommendations."
        )

    recommendations = get_recommend(movie_name)
    selected_movie = fetch_movie_details(movie_name)
    error_message = None

    if not recommendations:
        error_message = f"Sorry, we couldn't find recommendations for \"{movie_name}\". Try another title."

    return render_template(
        'index.html',
        movie_list=movies['title'].tolist(),
        recommendations=recommendations,
        selected_movie=selected_movie,
        search_query=movie_name,
        error_message=error_message,
        current_year=datetime.utcnow().year
    )


@app.route('/movie/<path:movie_title>')
def movie_detail(movie_title):
    movie = fetch_movie_details(movie_title)

    if not movie:
        return render_template(
            'movie_detail.html',
            movie_list=movies['title'].tolist(),
            movie=None,
            recommendations=[],
            error_message="We couldn't find details for that movie. Try searching for another title.",
            current_year=datetime.utcnow().year
        ), 404

    more_like_this = get_recommend(movie['title'])

    return render_template(
        'movie_detail.html',
        movie_list=movies['title'].tolist(),
        movie=movie,
        recommendations=more_like_this,
        error_message=None,
        current_year=datetime.utcnow().year
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)