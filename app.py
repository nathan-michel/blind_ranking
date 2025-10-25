# app.py
import streamlit as st
import random
import pandas as pd
import os
import io 
import requests # <-- Import nécessaire
from PIL import Image, ImageDraw, ImageFont, ImageOps # <-- ImageOps ajouté (au cas où, même si LANCZOS est dans Image)

# Configuration de l'application
st.set_page_config(page_title="Blind Ranker Custom", layout="centered")

# --- NOUVELLE FONCTION ---
@st.cache_data
def charger_et_redimensionner_image(url, max_hauteur=400):
    """
    Télécharge une image depuis une URL, la redimensionne à une hauteur 
    maximale en gardant le ratio, et la retourne en tant que bytes PNG.
    """
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        img = Image.open(io.BytesIO(response.content))
        
        width, height = img.size
        
        if height > max_hauteur:
            ratio = max_hauteur / height
            new_width = int(width * ratio)
            img = img.resize((new_width, max_hauteur), Image.LANCZOS)
        
        # --- MODIFICATION ICI ---
        # Convertir l'objet Image PIL redimensionné en bytes PNG
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
        # --- FIN MODIFICATION ---
    
    except Exception as e:
        print(f"Erreur lors du chargement/redimensionnement de l'image {url}: {e}")
        # En cas d'échec, on retourne l'URL originale
        return url

# --- FONCTIONS HELPERS (Génération de résultat) ---

def generer_texte_classement(slots):
    """Génère une chaîne de caractères simple pour le classement."""
    lignes = [f"Mon Classement - {st.session_state.categorie_active}\n", "--------------------------\n"]
    for i in range(1, 11):
        lignes.append(f"{i}. {slots[i]['Item']}\n") 
    return "".join(lignes)

def generer_image_classement(slots):
    """Génère une image PNG du classement."""
    W, H = 800, 600
    BG_COLOR = "white"
    TEXT_COLOR = "black"
    PADDING = 40
    FONT_PATH = "DejaVuSans.ttf" 

    img = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    try:
        font_titre = ImageFont.truetype(FONT_PATH, size=40)
        font_ligne = ImageFont.truetype(FONT_PATH, size=30)
    except IOError:
        st.error(f"Erreur : Fichier police '{FONT_PATH}' introuvable. Les accents/émojis ne s'afficheront pas.")
        font_titre = ImageFont.load_default()
        font_ligne = ImageFont.load_default()

    titre = f"Mon Classement - {st.session_state.categorie_active}"
    draw.text((PADDING, PADDING), titre, fill=TEXT_COLOR, font=font_titre)

    y = PADDING + 80
    for i in range(1, 11):
        texte_ligne = f"{i}. {slots[i]['Item']}" 
        draw.text((PADDING, y), texte_ligne, fill=TEXT_COLOR, font=font_ligne)
        y += 40 
        
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- FONCTIONS DE LOGIQUE DU JEU ---

@st.cache_data
def charger_liste_items(fichier_csv, selection_aleatoire=False):
    """Charge un DataFrame (Nom + URL) depuis un fichier CSV."""
    if not os.path.exists(fichier_csv):
        st.error(f"Erreur : Le fichier {fichier_csv} est introuvable.")
        return None
    try:
        df = pd.read_csv(fichier_csv)
        if "Item" not in df.columns or "ImageURL" not in df.columns:
            st.error(f"Erreur : Le CSV doit avoir les colonnes 'Item' et 'ImageURL'.")
            return None
        
        placeholder_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Placeholder_view_vector.svg/681px-Placeholder_view_vector.svg.png"
        df["ImageURL"].fillna(placeholder_url, inplace=True)

        if selection_aleatoire:
            if len(df) < 10:
                st.warning(f"Attention : {fichier_csv} a moins de 10 items.")
                return None
            return df.sample(n=10) 
        else:
            if len(df) != 10:
                st.warning(f"Attention : {fichier_csv} ne contient pas 10 items.")
            return df.head(10) 
    except Exception as e:
        st.error(f"Impossible de lire le fichier {fichier_csv}: {e}")
        return None

def initialiser_jeu(items_df, nom_categorie):
    """Prépare le 'session_state' pour une nouvelle partie."""
    st.session_state.slots = {i: None for i in range(1, 11)}
    
    items_melanges = items_df.sample(frac=1).to_dict('records')
    
    st.session_state.items_a_placer = items_melanges
    st.session_state.index_actuel = 0
    st.session_state.categorie_active = nom_categorie

def placer_item(numero_place):
    """Assigne l'item actuel (dict) à la place choisie."""
    item_actuel = st.session_state.items_a_placer[st.session_state.index_actuel]
    st.session_state.slots[numero_place] = item_actuel
    st.session_state.index_actuel += 1

# --- FONCTIONS D'AFFICHAGE (PAGES) ---

# (Remplacez votre ancienne fonction afficher_page_selection par celle-ci)

def afficher_page_selection():
    """Affiche le menu principal de sélection des catégories."""
    st.title("Mon Blind Ranker Perso ! 🏆")
    st.subheader("Choisissez une catégorie pour commencer :")

    # --- NOUVELLE CATÉGORIE ---
    if st.button("Sojasun 🌿 (10 au hasard)", use_container_width=True, type="primary"):
        
        # --- MODIFICATION ICI ---
        # On lit le nouveau fichier CSV qui contient les URLs
        items_df = charger_liste_items("sojasun_complet.csv", selection_aleatoire=True) 
        # --- FIN MODIFICATION ---
        
        if items_df is not None:
            initialiser_jeu(items_df, "Sojasun 🌿")
            st.session_state.page = "jeu"
            st.rerun()

    # --- CATEGORIE EXISTANTE ---
    if st.button("Jeux de société 🎲 (10 au hasard)", use_container_width=True, type="primary"):
        items_df = charger_liste_items("bga_jeux_complet.csv", selection_aleatoire=True) 
        if items_df is not None:
            initialiser_jeu(items_df, "Jeux de société 🎲")
            st.session_state.page = "jeu"
            st.rerun()

def afficher_page_jeu():
    """Affiche l'interface du jeu (classement)."""
    
    if st.button("⬅️ Changer de catégorie"):
        st.session_state.page = "selection"
        st.rerun()

    if st.session_state.index_actuel >= len(st.session_state.items_a_placer):
        st.header("🎉 C'est terminé ! 🎉")
        st.write("Voici votre classement final :")
        
        for i in range(1, 11):
            st.success(f"**{i}.** {st.session_state.slots[i]['Item']}") 

        st.write("---")
        st.subheader("Partager votre résultat")

        final_slots = st.session_state.slots
        texte_resultat = generer_texte_classement(final_slots)
        image_resultat_bytes = generer_image_classement(final_slots)

        tab1, tab2 = st.tabs(["Partager en Texte 📄", "Partager en Image 🖼️"])

        with tab1:
            st.text_area("Copiez ce texte :", texte_resultat, height=300)
            st.download_button(
                label="📥 Télécharger en .txt",
                data=texte_resultat,
                file_name="mon_classement.txt",
                mime="text/plain"
            )

        with tab2:
            st.image(image_resultat_bytes, caption="Aperçu de votre classement")
            st.download_button(
                label="📥 Télécharger en .png",
                data=image_resultat_bytes,
                file_name="mon_classement.png",
                mime="image/png"
            )
        
        if st.button("Recommencer avec une autre catégorie", use_container_width=True, type="primary"):
            st.session_state.page = "selection"
            st.rerun()

    else:
        # --- LE JEU EST EN COURS ---

        item_actuel = st.session_state.items_a_placer[st.session_state.index_actuel]
        
        st.header(f"Placez cet item :")
        
        # --- MODIFICATION ICI ---
        
        # Charger et redimensionner l'image, cela retourne des bytes PNG ou l'URL
        image_data_or_url = charger_et_redimensionner_image(item_actuel['ImageURL'], max_hauteur=300) # Hauteur max ajustée à 300px pour tester
        
        # Définir une largeur maximale d'affichage dans Streamlit
        # Cela forcera Streamlit à afficher l'image à cette largeur,
        # en conservant son ratio (car l'objet PIL a déjà été redimensionné ou Streamlit gère l'URL).
        MAX_DISPLAY_WIDTH = 100 # Par exemple, afficher à 100 pixels de large

        # Si c'est des bytes (image redimensionnée), on l'affiche directement
        if isinstance(image_data_or_url, bytes):
            st.image(image_data_or_url, width=MAX_DISPLAY_WIDTH) 
        # Si c'est l'URL (en cas d'échec de redimensionnement), Streamlit la gérera comme avant
        else: 
            st.image(image_data_or_url, width=MAX_DISPLAY_WIDTH) # Utilisez width ici aussi

        # --- FIN MODIFICATION ---
        
        st.title(f"{item_actuel['Item']}")
        
        st.write("---")
        st.subheader("Votre classement actuel :")

        for i in range(1, 11):
            place = st.session_state.slots[i]
            
            if place is None:
                if st.button(f"**{i}.** ❓ ... *Placer ici* ❓", key=f"slot_{i}", use_container_width=True):
                    placer_item(i)
                    st.rerun()
            else:
                st.info(f"**{i}.** {place['Item']}") 

# --- ROUTEUR PRINCIPAL DE L'APPLICATION ---
if 'page' not in st.session_state:
    st.session_state.page = "selection"

if st.session_state.page == "selection":
    afficher_page_selection()
elif st.session_state.page == "jeu":
    afficher_page_jeu()