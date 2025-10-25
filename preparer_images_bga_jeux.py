# preparer_images.py
import requests
import pandas as pd
from lxml import etree
import time
import io

INPUT_CSV = "bga_jeux.csv"
OUTPUT_CSV = "bga_jeux_complet.csv" # Le nouveau fichier qui sera créé
BGG_API_SEARCH = "https://boardgamegeek.com/xmlapi2/search"
BGG_API_THING = "https://boardgamegeek.com/xmlapi2/thing"

def trouver_image_bgg(nom_jeu):
    """Interroge l'API BGG pour trouver l'URL de l'image d'un jeu."""
    print(f"Recherche de : {nom_jeu}...")
    try:
        # 1. Rechercher le jeu pour obtenir son ID
        search_params = {'query': nom_jeu, 'type': 'boardgame', 'exact': 1}
        response_search = requests.get(BGG_API_SEARCH, params=search_params)
        
        if response_search.status_code != 200:
            # Gérer le rate limit (429) ou autre erreur
            print(f"  -> Erreur API (Search) {response_search.status_code}")
            return None

        search_root = etree.parse(io.BytesIO(response_search.content)).getroot()
        
        items = search_root.findall('item')
        if not items:
            # Si la recherche exacte échoue, on tente une recherche non exacte
            print(f"  -> Recherche exacte échouée, nouvelle tentative...")
            search_params['exact'] = 0
            response_search = requests.get(BGG_API_SEARCH, params=search_params)
            
            if response_search.status_code != 200:
                print(f"  -> Erreur API (Search 2) {response_search.status_code}")
                return None
                
            search_root = etree.parse(io.BytesIO(response_search.content)).getroot()
            items = search_root.findall('item')
            
            if not items:
                print(f"  -> Aucun résultat trouvé pour '{nom_jeu}'.")
                return None

        game_id = items[0].get('id')
        
        # 2. Obtenir les détails du jeu (dont l'image) avec son ID
        thing_params = {'id': game_id}
        response_thing = requests.get(BGG_API_THING, params=thing_params)
        
        if response_thing.status_code != 200:
            print(f"  -> Erreur API (Thing) {response_thing.status_code}")
            return None
            
        thing_root = etree.parse(io.BytesIO(response_thing.content)).getroot()
        
        image_node = thing_root.find(".//image")
        if image_node is not None and image_node.text:
            image_url = image_node.text
            print(f"  -> Image trouvée !")
            return image_url
        else:
            print(f"  -> ID trouvé ({game_id}) mais pas de balise image.")
            return None

    except Exception as e:
        print(f"  -> Erreur durant la recherche pour '{nom_jeu}': {e}")
        return None
    finally:
        # --- MODIFICATION ---
        # Soyons TRÈS polis avec l'API, attendons 10 secondes.
        print("   (Pause de 10s pour respecter l'API...)")
        time.sleep(10)
        # --- FIN MODIFICATION ---

# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Erreur : Fichier '{INPUT_CSV}' non trouvé.")
        exit()

    # Tente de lire le fichier de sortie s'il existe déjà
    try:
        df_output = pd.read_csv(OUTPUT_CSV)
        print("Fichier de sortie trouvé. Reprise du travail sur les lignes manquantes.")
        # Fusionner pour garder les URL déjà trouvées
        df = pd.merge(df, df_output[['Item', 'ImageURL']], on='Item', how='left')
    except FileNotFoundError:
        print("Fichier de sortie non trouvé. Création d'une nouvelle colonne ImageURL.")
        df["ImageURL"] = None # Créer la colonne si elle n'existe pas

    # On ne remplit que les lignes où l'URL est manquante (NaN)
    for index, row in df[df['ImageURL'].isnull()].iterrows():
        nom_jeu = row['Item']
        image_url = trouver_image_bgg(nom_jeu)
        
        if image_url:
            df.at[index, 'ImageURL'] = image_url

    # Sauvegarder le nouveau CSV complet
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nTerminé ! Fichier '{OUTPUT_CSV}' créé/mis à jour.")
    print("N'oubliez pas de 'push' ce nouveau fichier sur GitHub.")