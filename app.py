import streamlit as st
import pickle
import pandas as pd
import requests
import time

# Load data
movies = pickle.load(open('movies_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
content_similarity = pickle.load(open('content_similarity.pkl', 'rb'))

# --- Page Config ---
st.set_page_config(page_title="Movie Recommender", layout="wide")

# --- Theme Toggle ---
st.sidebar.title("🌓 Theme Settings")
dark_mode = st.sidebar.toggle("Enable Dark Mode", value=False)

# --- CSS for Dark/Light Themes ---
if dark_mode:
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #121212;
            color: white;
        }
        .stSelectbox, .stButton > button {
            background-color: #333;
            color: white;
        }
        .themed-text {
            color: var(--text-color);
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #ffffff;
            color: black;
        }
        .themed-text {
            color: var(--text-color);
        }
        </style>
    """, unsafe_allow_html=True)

# --- TMDB Poster Fetching ---
def fetch_poster(movie_id):
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=your_api_key')
        data = response.json()
        if data.get('poster_path'):
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            return None
    except:
        return None

# --- Hybrid Recommendation Logic ---
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]

    # Collaborative filtering
    collab_scores = list(enumerate(similarity[index]))
    collab_scores = sorted(collab_scores, key=lambda x: x[1], reverse=True)[1:11]

    # Content-based filtering
    content_scores = list(enumerate(content_similarity[index]))
    content_scores = sorted(content_scores, key=lambda x: x[1], reverse=True)[1:11]

    # Combine scores
    combined_scores = {}
    for i, score in collab_scores:
        combined_scores[i] = combined_scores.get(i, 0) + 0.5 * score
    for i, score in content_scores:
        combined_scores[i] = combined_scores.get(i, 0) + 0.5 * score

    # Final top 5 recommendations
    final_scores = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:5]

    recommend_movie = []
    recommend_poster = []
    for i, _ in final_scores:
        movie_id = movies.iloc[i].id
        title = movies.iloc[i].title
        poster = fetch_poster(movie_id)
        recommend_movie.append(title)
        recommend_poster.append(poster)
        time.sleep(0.2)

    return recommend_movie, recommend_poster

# --- App Title ---
st.title('🎬 Movie Recommender System (Hybrid)')
st.markdown("### 🎯 Recommended for You")

# --- Movie Select ---
st.markdown("#### <span class='themed-text'>🎥 Choose a movie to get recommendations:</span>", unsafe_allow_html=True)
selected_movie_name = st.selectbox("Choose a movie:", movies['title'].values, label_visibility="collapsed")


# --- Recommend Button ---
if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            if posters[i]:
                st.image(posters[i], use_container_width=True)
            else:
                st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True)
            st.caption(names[i])
