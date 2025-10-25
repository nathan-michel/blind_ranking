# preparer_images_sojasun.py
import requests
import pandas as pd
from lxml import html # Utilise html de lxml pour parser le HTML
import time
import io
from urllib.parse import quote_plus # Pour formater les URL de recherche

INPUT_CSV = "sojasun.csv"
OUTPUT_CSV = "sojasun_complet.csv" # Le nouveau fichier qui sera créé
SOJASUN_SEARCH_URL = "https://www.sojasun.com/" # L'URL de recherche est ?s=...

# Un "User-Agent" pour faire croire que nous sommes un navigateur
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def trouver_image_sojasun(nom_produit):
    """Interroge le site sojasun.com pour trouver l'URL de l'image d'un produit."""
    print(f"Recherche de : {nom_produit}...")
    try:
        # 1. Rechercher le produit sur le site
        # quote_plus encode les espaces et les accents pour l'URL
        search_params = {'s': nom_produit.encode('utf-8')}
        response_search = requests.get(SOJASUN_SEARCH_URL, params=search_params, headers=HEADERS)
        
        response_search.raise_for_status() # Lève une erreur si la requête échoue

        # Parser la page de résultats de recherche
        doc_search = html.fromstring(response_search.content)
        
        # On cherche le premier lien de produit dans les résultats
        # XPath : trouve une balise <a> dont le lien contient '/produit/'
        liens_produit = doc_search.xpath("//a[contains(@href, '/produit/')]/@href")
        
        if not liens_produit:
            print(f"  -> Aucun résultat trouvé pour '{nom_produit}'.")
            return None

        # On prend le premier lien
        page_produit_url = liens_produit[0]
        
        # 2. Visiter la page du produit pour trouver l'image
        print(f"  -> Page trouvée : {page_produit_url}")
        response_produit = requests.get(page_produit_url, headers=HEADERS)
        response_produit.raise_for_status()
        
        doc_produit = html.fromstring(response_produit.content)
        
        # L'image principale est souvent dans la balise "og:image"
        # XPath : trouve la balise <meta> qui a l'attribut property='og:image' 
        # et récupère son attribut 'content'
        images = doc_produit.xpath("//meta[@property='og:image']/@content")
        
        if images:
            image_url = images[0]
            print(f"  -> Image trouvée !")
            return image_url
        else:
            print(f"  -> Page produit trouvée mais pas de balise 'og:image'.")
            return None

    except Exception as e:
        print(f"  -> Erreur durant la recherche pour '{nom_produit}': {e}")
        return None
    finally:
        # Soyons polis, attendons 2 secondes
        print("   (Pause de 2s...)")
        time.sleep(2)

# --- SCRIPT PRINCIPAL ---
if __name__ == "__main__":
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Erreur : Fichier '{INPUT_CSV}' non trouvé.")
        exit()
        
    if "ImageURL" not in df.columns:
        df["ImageURL"] = None # Créer la colonne si elle n'existe pas

    # On ne remplit que les lignes où l'URL est manquante
    for index, row in df[df['ImageURL'].isnull()].iterrows():
        nom_produit = row['Item']
        image_url = trouver_image_sojasun(nom_produit)
        
        if image_url:
            df.at[index, 'ImageURL'] = image_url

    # Sauvegarder le nouveau CSV complet
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nTerminé ! Fichier '{OUTPUT_CSV}' créé.")
    print("N'oubliez pas de 'push' ce nouveau fichier sur GitHub.")
    print("Pensez à mettre à jour 'app.py' pour utiliser ce fichier.")