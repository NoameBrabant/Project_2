import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import os
import base64
from datetime import datetime
from streamlit_image_select import image_select
from Library import recommend_similar_films, id_movie_actor, id_movie_director

# Configuration de la page
st.set_page_config(page_title="Cinema Planet", layout="wide")

#Style CSS 
st.markdown("""
    <style>
        /* Style général */
        .stApp {background-color: #0B0D0E;}

        /* Titre principal */
        .gradient-text {
        background: linear-gradient(to right,#81BCCC 0%,#D8E7EB 50%,#082830 100%);
        background-size: 200% auto;
        color: transparent;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        padding: 20px;}
        @keyframes shine {to {background-position: 200% center;}}
        
        /* Sous-titres */
        .sub-title {
        color: #D8E7EB;
        font-size: 1.8rem;
        margin: 1.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #082830;}

        /* Images films*/
        .movie-card{
        background: #0B1012;
        border: 2px solid #082830;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(129, 188, 204, 0.2);
        transition: transform 0.3s ease;
        color: #D8E7EB;}
        .movie-card:hover {transform: translateY(-5px);
        border-color: ##81BCCC;
        cursor: pointer;}
        
        /* Overview */
        .synopsis-box {
        background: #0B1012;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #082830;
        margin: 1rem 0;
        color: #D8E7EB;}
        
        /* Barre Menu */
        .sidebar-content {
        background-color: #0B1012;
        border-right: 2px solid #082830;
        color: #D8E7EB;} 
        
        /* Selectbox */
        .stSelectbox {background-color: #082830; color: #D8E7EB;}
        /* Customize selectbox */
        div[data-baseweb="select"] > div {
        background-color: #0B1012;
        border-color: #082830;
        color: #D8E7EB;}
            
        /* Text elements */
        .stMarkdown, .stText {color: #D8E7EB;}
        
        /* Info boxes */
        .stInfo {background-color: #082830; color: #D8E7EB;}
        
        /* Liens */
        a {color: #D8E7EB}
        a:hover {color: #D8E7EB;}
            
        /* Boutons */
        .stButton > button {
        width: 100%;                    
        background-color: #0B1012;      
        color: #81BCCC;                   
        border-radius: 5px;             
        border: none;                  
        padding: 8px 16px;              
        margin: 5px auto;               
        font-size: 12px;               
        transition: all 0.3s;}
        /* Effet au survol */
        .stButton > button:hover {
        color: #81BCCC !important;
        background-color: #161C1F;}
        /* Effet au clic */                  
       .stButton > button:active,
       .stButton > button:focus {
       transform: translateY(0px);     
       background-color: #5A8B98;
       color: #082830 !important;}
       /* État visité */
       .stButton > button:visited {
       color: #81BCCC !important;} 
    </style>
    """, unsafe_allow_html=True)

#Ajout du logo:  
col1, col2 = st.columns([1, 2]) 
with col1:
    st.image('media\logo.png', width=500)  
with col2:      
    st.image('media\logo_2.png', width=1000) 

#Chargement du df_final et df_annexes:
file_path = 'ignore\df_final.parquet'
url_actor = 'ignore\df_actor.parquet'
url_real = 'ignore\df_director.parquet'
db = pd.read_parquet(file_path)
db_acteur = pd.read_parquet(url_actor)
db_real = pd.read_parquet(url_real)

#Page streamlit:
#Menu side :
with st.sidebar:
    selection_menu = option_menu(
        menu_title=None,
        options=["Accueil", "Acteurs", "Réalisateurs"],
        icons=["house", "person-fill", "camera-video-fill"],
        menu_icon="cast",
        styles={
            "container": {"background-color": "#0B0D0E"},
            "icon": {"color": "#D8E7EB"},
            "nav-link": {"color": "#D8E7EB","--hover-color": "#082830"},
            "nav-link-selected": {"background-color": "#0B0D0E"},})

#Initialisation de session_state
if 'selectbox_key' not in st.session_state:
    st.session_state.selectbox_key = "Entrez ou sélectionnez un film"

#Page d'accueil
if selection_menu == "Accueil":  
    st.markdown('<p class="gradient-text">Découvrez votre prochain coup de coeur</p>', unsafe_allow_html=True) 
    st.markdown('<h2 class="sub-title">Obtenez des recommandations de films personnalisées</h2>', unsafe_allow_html=True)  
    #Sélection d'un film avec le menu déroulant
    film = db['title'].sort_values(ascending=True).unique()
    film_with_blank = ["Entrez ou sélectionnez un film"] + list(film)
    #Paramètres pour rendre la selectbox modifiable 
    if 'button_clicked' in st.session_state:
        st.session_state.selectbox_key = st.session_state.button_clicked
        del st.session_state.button_clicked
    choix = st.selectbox(" ", film_with_blank, key='selectbox_key')
    if choix != "Entrez ou sélectionnez un film":
        
        #Ajout du jingle 
        audio_file = "media\jingle.mp3"
        with open(audio_file, "rb") as file:
            audio_data = file.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8') # Convertir les données audio en base64
        st.markdown(f"""
            <audio autoplay hidden>
                <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mpeg">
            </audio>
            """, unsafe_allow_html=True)
        
        #Aligner l'image et l'overview:
        col1, col2 = st.columns([1, 2])
        with col1:
            # Afficher l'image du film:
            poster_path = db.loc[db['title'] == choix, 'poster_path'].values[0]
            base_url = "https://image.tmdb.org/t/p/w500"
            poster_url = base_url + poster_path
            st.image(poster_url, caption=choix, width=250)
        
        with col2:
            #Afficher l'overview
            description = db.loc[db['title'] == choix, 'overview'].values[0]
            date = db.loc[db['title'] == choix, 'release_year'].values[0]
            director = db.loc[db['title'] == choix, 'name_director'].values[0]
            acteurs = db.loc[db['title'] == choix, ['actor_name_1', 'actor_name_2', 'actor_name_3', 'actor_name_4', 'actor_name_5']].values[0]
            acteurs_formates = ", ".join([f" {acteur} " for acteur in acteurs])
            st.markdown(f"""
                    <div class="synopsis-box">
                        <h3 style="color: #81BCCC; margin-bottom: 1rem;">Synopsis</h3>
                        <p>{description}</p>
                        <p style="color: #81BCCC; margin-top: 1rem;">Année de sortie : {date}</p>
                        <p style="color: #81BCCC; margin-top: 1rem;">Réalisateur : {director}</p>
                        <p style="color: #81BCCC; margin-top: 1rem;">Acteurs : {acteurs_formates}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        #Fonction pour obtenir les recommandations
        recommandations = recommend_similar_films(choix)
        #Afficher les films recommandés: afficher les images + titres 
        st.markdown('<h2 class="sub-title">Films Recommandés</h2>', unsafe_allow_html=True)
        cols = st.columns(5)
        for i, film_recommande in enumerate(recommandations):
            title_recommande = db.loc[db['id_movie'] == film_recommande, 'title'].values[0]
            poster_path = db.loc[db['title'] == title_recommande, 'poster_path'].values[0]
            base_url = "https://image.tmdb.org/t/p/w500"
            poster_url = base_url + poster_path
            with cols[i]:
                    st.markdown(f"""
                    <div class="movie-card">
                    <img src="{poster_url}" 
                    style="width: 100%; border-radius: 5px;">
                    </div> """, unsafe_allow_html=True)
                    #Rendre l'image cliquable pour retourner le film sélectionné en choix 
                    if st.button(title_recommande, key=f"rec_{i}"):
                        st.session_state.button_clicked = title_recommande
                        st.rerun()

    # Affichage Top 10 films
    current_year = datetime.now().year
    films_2024 = db[(db['release_date'].dt.year == current_year)]
    top_10 = films_2024.sort_values("vote_average", ascending=False).head(10)
    st.markdown('<h2 class="sub-title">Top 10 Films 2024</h2>', unsafe_allow_html=True)
    cols = st.columns(5)
    for i, (index, row) in enumerate(top_10.iterrows()):
        col_index = i % 5
        with cols[col_index]:
            st.markdown(f"""
            <div class="movie-card">
                <img src="https://image.tmdb.org/t/p/w500{row['poster_path']}" 
                    style="width: 100%; border-radius: 5px;">
            </div> """, unsafe_allow_html=True)
            #Rendre l'image cliquable pour retourner le film sélectionné en choix
            if st.button(row['title'], key=f"top_{i}"):
                st.session_state.button_clicked = row['title']
                st.rerun()

#Page des Acteurs:
elif selection_menu == "Acteurs":
    st.title("Vous pouvez choisir un acteur: ")
    acteur= db_acteur['name'].sort_values(ascending=True).unique()
    acteur_with_blank = [" "] + list(acteur)
    choix_acteur = st.selectbox(" ", acteur_with_blank)

    if choix_acteur != " ":
        col1, col2 = st.columns([1, 2])
        with col1:
            # Afficher photo de l'acteur:
            poster_path = db_acteur.loc[db_acteur['name'] == choix_acteur, 'profile_path'].values[0]
            base_url = "https://image.tmdb.org/t/p/w500"
            poster_url = base_url + poster_path
            st.image(poster_url, caption=choix_acteur)
        
        with col2: 
            films_acteur = id_movie_actor(choix_acteur, db)
            cols_per_row = 5
            for idx, film_id in enumerate(films_acteur):
                if idx % cols_per_row == 0:
                    cols = st.columns(cols_per_row)

                title_film = db.loc[db['id_movie'] == film_id, 'title'].values
                poster_path = db.loc[db['id_movie'] == film_id, 'poster_path'].values

                # Gestion des valeurs manquantes
                title_film = title_film[0] if len(title_film) > 0 else "Titre inconnu"
                poster_path = poster_path[0] if len(poster_path) > 0 else "default_image.jpg"

                # Construire l'URL du poster
                base_url = "https://image.tmdb.org/t/p/w500"
                poster_url = base_url + poster_path

                # Afficher dans la colonne correspondante
                with cols[idx % cols_per_row]:
                    st.markdown(f"""
                    <div class="movie-card">
                        <img src="{poster_url}" 
                        style="width: 100%; border-radius: 5px;">
                        <p style="text-align: center; margin-top: 0.5rem; font-weight: bold;">
                        {title_film}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

        # Afficher la page de l'acteur
        base_url_acteur = "https://www.imdb.com/name/"
        imdb_id = db_acteur.loc[db_acteur['name'] == choix_acteur, 'imdb_id'].values[0]
        url_acteur = base_url_acteur + imdb_id
        st.markdown(f"<a href='{url_acteur}' target='_blank' style='color: #D8E7EB;'>En savoir plus sur {choix_acteur}</a>", unsafe_allow_html=True)
    
    else :
        st.info("Veuillez sélectionner un acteur")

#Page des Réalisateurs:        
elif selection_menu == "Réalisateurs":
    st.title("Vous pouvez choisir un réalisateur: ")
    realisateur = db_real['name'].sort_values(ascending=True).unique()
    real_with_blank = [" "] + list(realisateur)
    choix_real = st.selectbox(" ", real_with_blank)
    
    if choix_real != " ":
        col1, col2 = st.columns([1, 2])
        with col1:
            #Afficher photo du réal 
            poster_path = db_real.loc[db_real['name'] == choix_real, 'profile_path'].values[0]
            base_url = "https://image.tmdb.org/t/p/w500"
            poster_url = base_url + poster_path
            st.image(poster_url, caption=choix_real)

        with col2: 
            #Afficher les films du réalisteur:
            film_director = id_movie_director(choix_real, db)
            cols_per_row = 5
            for idx, film_id in enumerate(film_director):
                if idx % cols_per_row == 0:
                    cols = st.columns(cols_per_row)

                title_film = db.loc[db['id_movie'] == film_id, 'title'].values
                poster_path = db.loc[db['id_movie'] == film_id, 'poster_path'].values

                # Gestion des valeurs manquantes
                title_film = title_film[0] if len(title_film) > 0 else "Titre inconnu"
                poster_path = poster_path[0] if len(poster_path) > 0 else "default_image.jpg"

                # Construire l'URL du poster
                base_url = "https://image.tmdb.org/t/p/w500"
                poster_url = base_url + poster_path

                # Afficher dans la colonne correspondante
                with cols[idx % cols_per_row]:
                    st.markdown(f"""
                    <div class="movie-card">
                        <img src="{poster_url}" 
                        style="width: 100%; border-radius: 5px;">
                        <p style="text-align: center; margin-top: 0.5rem; font-weight: bold;">
                        {title_film}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
            
        #Afficher la page  du réal
        base_url_real = "https://www.imdb.com/name/"
        imdb_id = db_real.loc[db_real['name'] == choix_real, 'imdb_id'].values[0]
        url_real = base_url_real + imdb_id
        st.markdown(f"<a href='{url_real}' target='_blank' style='color: #D8E7EB;'>En savoir plus sur {choix_real}</a>", unsafe_allow_html=True)

    else:
        st.info("Veuillez sélectionner un réalisateur")