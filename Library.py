import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from datetime import date
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, MultiLabelBinarizer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_array
import re

df_movie = pd.read_parquet("ignore\df_movie.parquet")
pd.set_option('display.max_columns', None)

numeric_cols = ['popularity_movie', 'vote_average', 'vote_count',
       'gender_director', 'popularity_director', 'birthday_director', 'actor_2_mean_movie', 'actor_3_mean_movie',
       'actor_4_mean_movie', 'actor_5_mean_movie', 'actor_gender_1',
       'actor_gender_2', 'actor_gender_3', 'actor_gender_4', 'actor_gender_5',
       'actor_popularity_1', 'actor_popularity_2', 'actor_popularity_3',
       'actor_popularity_4', 'actor_popularity_5']


categorical_cols = ['original_language', 'name_director', 'place_of_birth_director']

binarizer_cols = ['genre']

date_cols = ['release_date', 'birthday_director', 'deathday_director']

# Custom transformer for MultiLabelBinarizer
class MultiLabelBinarizerPipelineFriendly(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.mlb = MultiLabelBinarizer()

    def fit(self, X, y=None):
        self.mlb.fit(X)
        return self

    def transform(self, X):
        return self.mlb.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self.mlb.classes_
    
numeric_transformer = Pipeline(steps=[
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

date_transformer = Pipeline(steps=[
    ('date', OrdinalEncoder())
])

# On combine tout dans un ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_cols),
        ('cat', categorical_transformer, categorical_cols),
        ('genres', MultiLabelBinarizerPipelineFriendly(), 'genre'),
        ('date', date_transformer, date_cols)
    ]
)

pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor)
])

# Transformation des données
processed_data = pipeline.fit_transform(df_movie)

# Affichage des données transformées
transformed_df = pd.DataFrame(processed_data.todense(), columns=pipeline["preprocessor"].get_feature_names_out())

# Initialisation du modèle KNN
knn_model = NearestNeighbors(n_neighbors=6, metric='manhattan')  # 5 voisins les plus proches hormis le point de référence lui meme
knn_model.fit(processed_data)

# Fonction recommandation pour un item
def recommend_similar_films(title, 
                              data: pd.DataFrame=processed_data, 
                              model: NearestNeighbors=knn_model, 
                              original_data: pd.DataFrame=df_movie, 
                              n_neighbors: int=6) -> tuple[list[float], list[float]]:
    """
    Trouve les n éléments les plus proches pour un élément donné.

    Args:
        title: le titre d'un film
        data: Données transformées utilisées pour KNN = df processed data
        model: Modèle KNN pré-entraîné.
        original_data: Données originales (pour affichage) = df movies
        n_neighbors: Nombre de voisins à recommander = 6 pour avoir 5 recommandations

    Returns:
        films similaires: Indices et distances des filmes similaires.
    """
    index = original_data[original_data['title'] == title].index[0] # l'indice du film recherché 
    distances, indices = model.kneighbors(data[index], n_neighbors=n_neighbors) 
    
    indices = indices[0][1:]
    id_movie = [int(original_data.loc[i, 'id_movie']) for i in indices] 
    return id_movie

# Fonction pour afficher les films des acteurs 
def id_movie_actor(name_actor: str, df: pd.DataFrame) -> int: 
    current = {}

    for i in range(1, 6): 
        col_name = f"actor_name_{i}"
        temp = {}
        df_current = df.groupby(col_name)['id_movie'].agg(list)
        df_current = pd.DataFrame(df_current)
        df_current = df_current.reset_index()
        
        for y in range(0, len(df_current)):
            name = df_current.loc[y, col_name]
            temp[name] = df_current.loc[y, 'id_movie']
        
        for k, v in temp.items():
            if k in current: 
                current[k] += temp[k]
            else: 
                current[k] = temp[k]
    return current[name_actor]

# Fonction pour afficher les films du director
def id_movie_director(name_director: str, df: pd.DataFrame) -> int: 
    df_current = df.groupby('name_director')['id_movie'].agg(list)
    df_current = pd.DataFrame(df_current)
    df_current = df_current.reset_index()
    index = df_current[df_current['name_director'] == name_director].index
    return list(df_current.loc[index, 'id_movie'])[0]