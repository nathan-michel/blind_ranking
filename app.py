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
# Injection CSS dans app.py
st.markdown("""       
    <style>
        /* 1. RÉSERVATION D'ESPACE (Ratio 5:3) */
        /* On force le conteneur à avoir une hauteur proportionnelle à sa largeur */
        [data-testid="stImage"] {
            background-color: white;
            border-radius: 10px;
            /* On fixe la hauteur pour éviter le "saut" au chargement */
            min-height: 200px; 
            max-height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }

        /* 2. STABILISATION DU TITRE */
        /* On donne une hauteur minimale au titre de l'item pour éviter qu'il ne bouge */
        .item-title-container {
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: left;
            text-align: center;
        }

        /* 3. MASQUER LES ÉLÉMENTS STREAMLIT ET ANCRES */
        header, footer, .stDeployButton, a.anchor-link { display:none !important; }

        /* 1. SUPPRESSION DU SUPERFLU (Header, Menu, Footer) */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}

        /* 2. OPTIMISATION DE L'ESPACE (Mobile First) */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 800px; /* Centre le contenu sur PC */
        }

        /* 3. STYLE DES BOUTONS (Général) */
        div.stButton > button {
            width: 100%;
            border-radius: 12px;
            height: 3.5em; /* Plus facile à cliquer au pouce */
            font-size: 16px !important;
            font-weight: 600;
            border: 1px solid #D1D5DB;
            transition: all 0.2s;
        }

        /* 4. FIX POUR LE CENTRAGE ET L'APPARENCE DES BOUTONS REMPLIS (Désactivés) */
        /* On force l'opacité et la couleur pour que ce soit lisible */
        button[disabled] {
            opacity: 1 !important;
            color: #1E1E2E !important; /* Texte bien noir/bleu nuit */
            background-color: #F0F2F6 !important; /* Fond gris très clair */
            border: 1px solid #D1D5DB !important;
            cursor: default !important;
            box-shadow: none !important;
        }
        
        /* Assure que le texte à l'intérieur du bouton désactivé reste centré */
        button[disabled] p {
            color: #1E1E2E !important;
            text-align: center !important;
            width: 100%;
        }

        /* 5. ADAPTATION DES TITRES SUR MOBILE */
        @media (max-width: 768px) {
            h1 {
                font-size: 1.5rem !important;
                text-align: center;
            }
            h2, h3 {
                font-size: 1.2rem !important;
                text-align: center;
            }
            /* Réduction légère de la taille du texte dans les boutons sur petit écran */
            div.stButton > button {
                font-size: 14px !important;
            }
        }


        /* 5. Images pas en full screen */    
        button[title="View fullscreen"]{
            visibility: hidden;
        }
            

        /* 1. SUPPRESSION TOTALE DES MARGES SUPÉRIEURES */
        .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0rem !important;
            max-width: 600px;
        }

        /* 2. RÉDUCTION DES ESPACES ENTRE TOUS LES ÉLÉMENTS (Vertical Block) */
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }

        /* 3. STABILISATION ET CADRE IMAGE COMPACT */
        [data-testid="stImage"] {
            background-color: white;
            border-radius: 12px;
            min-height: 180px; /* Réduit pour gagner de la place */
            display: flex; align-items: center; justify-content: center;
        }

        /* 4. TITRES ET TEXTES COMPACTS */
        .item-title-container {
            min-height: 50px; /* Divisé par 2 */
            margin: 0 !important;
            padding: 0 !important;
        }
        
        h1 { font-size: 1.4rem !important; margin: 0 !important; }
        h2, h3 { font-size: 1.1rem !important; margin: 0 !important; }

        /* 5. BOUTONS DE CLASSEMENT SERRÉS */
        div.stButton > button {
            border-radius: 8px;
            height: 2.8em !important; /* Plus fin */
            margin-bottom: -10px !important;
        }

        /* Masquer les ancres et le superflu */
        header, footer, .stDeployButton, a.anchor-link { display: none !important; }

    </style>
""", unsafe_allow_html=True)

## Injection de CSS pour le mobile
#st.markdown("""
#    
#    <style>
#        /* Supprimer les marges excessives en haut */
#        .block-container {
#            padding-top: 1rem;
#            padding-bottom: 0rem;
#            padding-left: 1rem;
#            padding-right: 1rem;
#        }
#        
#        /* Rendre les titres plus compacts sur mobile */
#        h1 {
#            font-size: 1.8rem !important;
#            text-align: center;
#        }
#        
#        /* Styliser les boutons de classement pour qu'ils soient plus grands (tactile) */
#        div.stButton > button {
#            border-radius: 10px;
#            height: 3em;
#            font-size: 16px !important;
#            margin-bottom: -10px;
#        }
#        
#        /* Cacher le menu Streamlit et le footer par défaut pour gagner de la place */
#        #MainMenu {visibility: hidden;}
#        footer {visibility: hidden;}
#        header {visibility: hidden;}
#    </style>
#""", unsafe_allow_html=True)




#@st.cache_data
#def charger_et_redimensionner_image(url, cible_w=500, cible_h=300):
#    """Télécharge et force l'image dans un canevas de taille fixe."""
#    try:
#        response = requests.get(url, timeout=10)
#        response.raise_for_status()
#        img = Image.open(io.BytesIO(response.content)).convert("RGB")
#        
#        # ImageOps.pad redimensionne et centre l'image dans le rectangle cible
#        # sans la déformer et en ajoutant des bordures si nécessaire.
#        img_fixed = ImageOps.pad(img, (cible_w, cible_h), color="white")
#        
#        img_byte_arr = io.BytesIO()
#        img_fixed.save(img_byte_arr, format='PNG')
#        return img_byte_arr.getvalue()
#    except Exception as e:
#        # En cas d'erreur, on crée un rectangle blanc vide de la même taille
#        img_error = Image.new('RGB', (cible_w, cible_h), color="white")
#        buf = io.BytesIO()
#        img_error.save(buf, format='PNG')
#        return buf.getvalue()
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

    st.title("BLIND RANKING CLUB MARRAKECH ! 🏆", anchor=False)
    
    # --- SECTION DAILY ---
    st.subheader("📅 Le Défi du Jour", anchor=False)
    st.write(f"Même liste pour tout le monde ! (Date : {datetime.date.today().strftime('%d/%m/%Y')})")
    
    # On utilise la graine du jour pour les jeux de société
    if st.button("JEUX DE SOCIÉTÉ : DAILY CHALLENGE 🔥", use_container_width=True, type="primary"):
        demarrer_partie("bga_jeux_complet.csv", "Daily Jeux de Société 📅", seed=graine_du_jour)

    st.write("---")

    # --- SECTION CLASSIQUE ---
    st.subheader("🚀 Catégories Libres", anchor=False)
    
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
        st.header("🎉 C'est terminé ! 🎉", anchor=False)
        #st.write("Voici votre classement final :")
        #
        #for i in range(1, 11):
        #    st.success(f"**{i}.** {st.session_state.slots[i]['Item']}") 
#
        #st.write("---")
        st.subheader("Partager votre résultat", anchor=False)

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
            for i in range (45):
                st.write("")
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
        
        st.header(f"Placez cet item :", anchor=False)
        
        # Charger et redimensionner l'image, cela retourne des bytes PNG ou l'URL
        image_data_or_url = charger_et_redimensionner_image(item_actuel['ImageURL'])#, max_hauteur=300) # Hauteur max ajustée à 300px pour tester
        
        # Définir une largeur maximale d'affichage dans Streamlit
        # Cela forcera Streamlit à afficher l'image à cette largeur,
        # en conservant son ratio (car l'objet PIL a déjà été redimensionné ou Streamlit gère l'URL).
        MAX_DISPLAY_WIDTH = 120 # Par exemple, afficher à 100 pixels de large

        # Si c'est des bytes (image redimensionnée), on l'affiche directement
        if isinstance(image_data_or_url, bytes):
            st.image(image_data_or_url, width=MAX_DISPLAY_WIDTH) 
        # Si c'est l'URL (en cas d'échec de redimensionnement), Streamlit la gérera comme avant
        else: 
            st.image(image_data_or_url, width=MAX_DISPLAY_WIDTH) # Utilisez width ici aussi
        
        st.markdown(f"""
            <div class="item-title-container">
                <h1 style="margin:0; padding:0;">{item_actuel['Item']}</h1>
            </div>
        """, unsafe_allow_html=True)
        #st.title(f"{item_actuel['Item']}", anchor=False)
        

        # --- DANS afficher_page_jeu() ---
        st.write("---")
        st.subheader("Votre classement actuel :", anchor=False)

        # On crée deux colonnes pour que les boutons soient côte à côte (5 à gauche, 5 à droite)
        col1, col2 = st.columns(2)

        for i in range(1, 11):
            # On alterne entre col1 et col2
            cible_col = col1 if i <= 5 else col2

            with cible_col:
                place = st.session_state.slots[i]
                if place is None:
                    if st.button(f"**{i}.** ❓ ... *Placer ici* ❓", key=f"slot_{i}", use_container_width=True):
                        placer_item(i)
                        st.rerun()
                else:
                    st.button(f"**{i}.** {place['Item']}", key=f"filled_{i}", use_container_width=True, disabled=True)

        #st.write("---")
        #st.subheader("Votre classement actuel :", anchor=False)
#
        #for i in range(1, 11):
        #    place = st.session_state.slots[i]
        #    
        #    if place is None:
        #        if st.button(f"**{i}.** ❓ ... *Placer ici* ❓", key=f"slot_{i}", use_container_width=True):
        #            placer_item(i)
        #            st.rerun()
        #    else:
        #        st.info(f"**{i}.** {place['Item']}") 

# --- ROUTEUR PRINCIPAL DE L'APPLICATION ---
if 'page' not in st.session_state:
    st.session_state.page = "selection"

if st.session_state.page == "selection":
    afficher_page_selection()
elif st.session_state.page == "jeu":
    afficher_page_jeu()