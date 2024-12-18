import requests
import pandas as pd
import sys
from datetime import datetime, timedelta
import json
import time
import os
from dotenv import load_dotenv
import os

# Charger le fichier .env
load_dotenv()

# Récupérer les valeurs des variables d'environnement
api_key = os.getenv("KEY2")

print(f"API_KEY: {api_key}")
sys.exit()

url = "https://api.themoviedb.org/3/discover/movie"


parameters = {
    "language" : "fr-FR",
    "include_adult" : False,
    "include_video" : False,
    "page" : 1,
    "primary_release_date.lte" : "2020-01-01",
    "primary_release_date.gte" : "2010-01-01",
    "with_runtime.gte" : 45,
    "with_runtime.lte" : 240,
}

headers = {
    "accept": "application/json",
    "Authorization": "KEY2"
}


# print(os.getenv("KEY2"))
# sys.exit()

# recup de date der film


# Lire un fichier .parquet
df_movies = pd.read_parquet('df_final.parquet', engine='pyarrow')  # ou engine='fastparquet'
# print(df_movies)

# Trouver la plus grande date
max_date = df_movies['release_date'].max()
print("La plus grande date est :", max_date)

# sys.exit()

# Obtenir la date du jour
date_du_jour = datetime.now()

# Formater la date au format "aaaa-mm-jj"
date_du_jour_formattee = date_du_jour.strftime('%Y-%m-%d')

print("La date du jour est :", date_du_jour_formattee)


# Conversion en objet datetime
date_obj = datetime.strptime(max_date, "%Y-%m-%d")

# Ajout d'un jour
new_date = date_obj + timedelta(days=1)

# Conversion en chaîne de caractères
max_date_formattee = new_date.strftime("%Y-%m-%d")

#recup des films entre date du jour et dernière date dans le fichier parquet
flag=""
parameters["primary_release_date.lte"] = f"{date_du_jour_formattee}"
parameters["primary_release_date.gte"] = f"{max_date_formattee}"
#ne pas continuer et dire que les données sont ajour si max_date_formattee>date_du_jour_formattee

try:
    while(True) :
        r = requests.get(url, headers=headers, params=parameters)
        # Charger le texte JSON en un dictionnaire Python
        response_data = r.json()
        # print(r.text)
        # Vérifier si "results" est une liste vide
        if "results" in response_data and response_data["results"]:
            flag="new_data"
            df_new = pd.json_normalize(json.loads(r.text), record_path="results")
            df_movies = pd.concat([df_movies, df_new], ignore_index=True)
            parameters["page"] += 1
            if parameters["page"] % 40 == 0:
                time.sleep(1)
            print(f"\rProgress: {parameters["page"]}, {parameters["primary_release_date.lte"]}", end='', flush=True)
        else:
            break
except Exception as e:
    if r.status_code == 400:
        parameters["page"] = 1
    else:
        print(r.status_code)

        print(f"Une erreur s'est produite : {e}")
        
# Sort by column: 'release_date' (descending)
print(df_movies["release_date"].max())
if flag=="new_data" :
    # Étape 3 : Sauvegarder les données dans un fichier Parquet
    df_movies.to_parquet('df_final.parquet', engine='pyarrow')
    print("Les données ont été sauvegardées dans 'df_final.parquet'")
else :
    print("Les données sont déjà à jour")
