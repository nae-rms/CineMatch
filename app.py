import os
import requests
import pickle
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# Load TMDB Read Access Token
load_dotenv()
API_TOKEN = os.getenv("TMDB_READ_TOKEN")

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

IMAGE_BASE_URL = "https://image.tmdb.org/t3/p/w500"

# Fetch poster path directly from TMDB using movie ID
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"{IMAGE_BASE_URL}{poster_path}"
    except Exception as e:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

# Load pickled model artifacts
movies_list = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Recommendation logic
def recommend(movie_title, top_n=5):
    movie_idx = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_idx]
    
    # Sort by similarity score descending
    sorted_sim = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    recommended_movies = []
    recommended_posters = []
    
    for i in sorted_sim:
        movie_data = movies.iloc[i[0]]
        recommended_movies.append(movie_data['title'])
        recommended_posters.append(fetch_poster(movie_data['id']))
        
    return recommended_movies, recommended_posters

# Streamlit UI Configuration
st.set_page_config(page_title="Movie Recommender System", layout="wide")
st.title("🎬 Movie Recommendation System")

# Dropdown for selecting a movie
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown:",
    movies['title'].values
)

if st.button("Show Recommendations"):
    names, posters = recommend(selected_movie)
    
    # Display top 5 recommendations in columns
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx], use_container_width=True)
            st.caption(f"**{names[idx]}**")