from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# Load movie data and similarity matrix
movies_list = pickle.load(open('Data/movies.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('Data/similarity.pkl', 'rb'))

# Your OMDb API Key
OMDB_API_KEY = 'e0585436'

# ✅ Function to fetch poster from OMDb API
def fetch_poster(movie_title):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_title}"
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get('Poster') and data['Poster'] != 'N/A':
            return data['Poster']
        else:
            return "https://via.placeholder.com/300x450.png?text=No+Poster"
    except Exception as e:
        print(f"❌ Error fetching poster for {movie_title}: {e}")
        return "https://via.placeholder.com/300x450.png?text=Error"

# ✅ Recommendation logic using cosine similarity
def get_recommend(movie_name):
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

# ✅ Flask Routes
@app.route('/')
def home():
    return render_template('index.html', movie_list=movies['title'].tolist())

@app.route('/recommend', methods=['POST'])
def recommend():
    movie_name = request.form.get('movie')
    recommendations = get_recommend(movie_name)
    return render_template(
        'index.html',
        movie_list=movies['title'].tolist(),
        recommendations=recommendations
    )

if __name__ == '__main__':
    app.run(debug=True)
