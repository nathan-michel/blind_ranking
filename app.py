import streamlit as st
import random
import pandas as pd
import os
import io 
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps 
import datetime

CATEGORIES = {
    "Sojasun 🌿": "sojasun_complet.csv",
    "Jeux de société 🎲": "bga_jeux_complet.csv",
}

aujourdhui = datetime.date.today()
graine_du_jour = int(aujourdhui.strftime('%Y%m%d'))

# Configuration de l'application
st.set_page_config(page_title="BLIND RANKING CLUB MARRAKECH", layout="centered")

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
        
        # Convertir l'objet Image PIL redimensionné en bytes PNG
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    
    except Exception as e:
        print(f"Erreur lors du chargement/redimensionnement de l'image {url}: {e}")
        # En cas d'échec, on retourne l'URL originale
        return url

# --- FONCTIONS HELPERS (Génération de résultat) ---

def generer_texte_classement(slots):
    """Génère un texte de partage élégant."""
    date_str = datetime.date.today().strftime('%d/%m/%Y')
    categorie = st.session_state.categorie_active
    
    # Header personnalisé si c'est le Daily
    if "Daily" in categorie:
        txt = f"🏆 **BLIND RANKING DAILY** 🏆\n📅 Défi du {date_str}\n\n"
    else:
        txt = f"🏆 **BLIND RANKING** 🏆\n📂 Catégorie : {categorie}\n\n"
    
    for i in range(1, 11):
        txt += f"{i}. {slots[i]['Item']}\n"
    
    txt += "\n🎮 Joue toi aussi sur : [Ton Lien Streamlit]"
    return txt

def generer_image_classement(slots):
    """Génère une carte de score au look professionnel."""
    W, H = 800, 930 # Format vertical plus moderne
    PRIMARY_COLOR = "#1E1E2E" # Bleu nuit profond
    CARD_COLOR = "#FFFFFF"     # Blanc pur pour les cartouches
    ACCENT_COLOR = "#FF4B4B"   # Rouge corail pour le badge
    TEXT_MAIN = "#1E1E2E"
    TEXT_SUB = "#585B70"
    
    img = Image.new('RGB', (W, H), color="#F2F4F7")
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("DejaVuSans.ttf", 42)
        font_med = ImageFont.truetype("DejaVuSans.ttf", 28)
        font_bold = ImageFont.truetype("DejaVuSans.ttf", 32)
    except:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_bold = ImageFont.load_default()

    # --- HEADER ---
    # Dessin d'un bandeau supérieur foncé
    draw.rectangle([0, 0, W, 180], fill=PRIMARY_COLOR)
    
    titre = "CLASSEMENT FINAL"
    draw.text((40, 45), titre, fill="white", font=font_big)
    
    # Sous-titre (Catégorie)
    cat_name = st.session_state.categorie_active.split("📅")[0].strip()
    draw.text((40, 105), cat_name, fill="#BAC2DE", font=font_med)

    # --- BADGE DAILY ---
    if "Daily" in st.session_state.categorie_active:
        date_str = datetime.date.today().strftime('%d/%m/%Y')
        # Dessin d'un badge arrondi (rectangle + texte)
        badge_rect = [W-220, 45, W-40, 135]
        draw.rounded_rectangle(badge_rect, radius=15, fill=ACCENT_COLOR)
        draw.text((W-195, 60), "DAILY", fill="white", font=font_med)
        draw.text((W-205, 95), date_str, fill="white", font=ImageFont.truetype("DejaVuSans.ttf", 22))

    # --- LISTE DES ITEMS (Cartouches) ---
    y_start = 220
    for i in range(1, 11):
        # Fond du cartouche de ligne
        rect = [40, y_start, W-40, y_start + 55]
        draw.rounded_rectangle(rect, radius=10, fill=CARD_COLOR, outline="#D1D5DB", width=1)
        
        # Numéro
        color_num = TEXT_SUB
        draw.text((60, y_start + 12), f"{i}.", fill=color_num, font=font_bold)
        
        # Texte de l'item
        item_text = slots[i]['Item']
        if len(item_text) > 40: item_text = item_text[:37] + "..."
        draw.text((120, y_start + 12), item_text, fill=TEXT_MAIN, font=font_med)
        
        y_start += 65

    # --- FOOTER ---
    draw.text((W/2 - 100, H - 40), "Généré par Blind Ranking CLUB MARRAKECH", fill=TEXT_SUB, font=ImageFont.truetype("DejaVuSans.ttf", 18))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# --- FONCTIONS DE LOGIQUE DU JEU ---

@st.cache_data
def charger_toute_la_liste(fichier_csv):
    """Charge l'intégralité du fichier CSV en cache."""
    if not os.path.exists(fichier_csv):
        st.error(f"Erreur : Le fichier {fichier_csv} est introuvable.")
        return None
    try:
        df = pd.read_csv(fichier_csv)
        placeholder_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Placeholder_view_vector.svg/681px-Placeholder_view_vector.svg.png"
        df["ImageURL"].fillna(placeholder_url, inplace=True)
        return df
    except Exception as e:
        st.error(f"Impossible de lire le fichier {fichier_csv}: {e}")
        return None
    
@st.cache_data
def charger_liste_items(fichier_csv):
    """Charge un DataFrame (Nom + URL) depuis un fichier CSV."""
    if not os.path.exists(fichier_csv):
        st.error(f"Erreur : Le fichier {fichier_csv} est introuvable.")
        return None
    try:
        df = pd.read_csv(fichier_csv)
        
        placeholder_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Placeholder_view_vector.svg/681px-Placeholder_view_vector.svg.png"
        df["ImageURL"].fillna(placeholder_url, inplace=True)

        return df
    except Exception as e:
        st.error(f"Impossible de lire le fichier {fichier_csv}: {e}")
        return None

def initialiser_jeu(items_df, nom_categorie, seed=None):
    """Prépare le 'session_state' pour une nouvelle partie."""
    st.session_state.slots = {i: None for i in range(1, 11)}
    
    items_melanges = items_df.to_dict('records')
    # Si une seed est fournie, on verrouille l'ordre du mélange
    if seed is not None:
        random.Random(seed).shuffle(items_melanges)
    else:
        random.shuffle(items_melanges) # Hasard total sinon

    st.session_state.items_a_placer = items_melanges
    st.session_state.index_actuel = 0
    st.session_state.categorie_active = nom_categorie

def demarrer_partie(fichier_csv, nom_affichage, seed=None):
    """Logique unique pour lancer n'importe quelle catégorie."""
    df_complet = charger_toute_la_liste(fichier_csv)
    if df_complet is not None:
        # On pioche 10 items au hasard
        selection_10 = df_complet.sample(n=min(10, len(df_complet)), random_state=seed)
        # On initialise le jeu avec cette sélection
        initialiser_jeu(selection_10, nom_affichage, seed=seed)
        # On change de page
        st.session_state.page = "jeu"
        st.rerun()

def placer_item(numero_place):
    """Assigne l'item actuel (dict) à la place choisie."""
    item_actuel = st.session_state.items_a_placer[st.session_state.index_actuel]
    st.session_state.slots[numero_place] = item_actuel
    st.session_state.index_actuel += 1

# --- FONCTIONS D'AFFICHAGE (PAGES) ---


def afficher_page_selection():

    st.title("BLIND RANKING CLUB MARRAKECH ! 🏆")
    
    # --- SECTION DAILY ---
    st.subheader("📅 Le Défi du Jour")
    st.write(f"Même liste pour tout le monde ! (Date : {datetime.date.today().strftime('%d/%m/%Y')})")
    
    # On utilise la graine du jour pour les jeux de société
    if st.button("JEUX DE SOCIÉTÉ : DAILY CHALLENGE 🔥", use_container_width=True, type="primary"):
        demarrer_partie("bga_jeux_complet.csv", "Daily Jeux de Société 📅", seed=graine_du_jour)

    st.write("---")

    # --- SECTION CLASSIQUE ---
    st.subheader("🚀 Catégories Libres")
    
    # On définit nos catégories classiques

    for nom, fichier in CATEGORIES.items():
        if st.button(nom, use_container_width=True):
            # Ici on ne passe pas de seed, donc c'est du pur hasard
            demarrer_partie(fichier, nom)            

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