import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont

# Création de la base de données
DB_PATH = "cybernotes.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                subcategory TEXT,
                title TEXT,
                content TEXT,
                image_path TEXT,
                created_by TEXT,
                last_modified_by TEXT
            )''')
conn.commit()

try:
    conn.execute("ALTER TABLE knowledge ADD COLUMN created_by TEXT DEFAULT 'Anonymous'")
    conn.execute("ALTER TABLE knowledge ADD COLUMN last_modified_by TEXT DEFAULT 'Anonymous'")
    conn.commit()
except sqlite3.OperationalError:
    pass  

# Fonction pour ajouter une nouvelle connaissance
def add_knowledge(category, subcategory, title, content, image_path=None, created_by="Anonymous"):
    c.execute("INSERT INTO knowledge (category, subcategory, title, content, image_path, created_by, last_modified_by) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (category, subcategory, title, content, image_path, created_by, created_by))
    conn.commit()

# Fonction pour récupérer les connaissances
def get_knowledge():
    df = pd.read_sql_query("SELECT * FROM knowledge", conn)
    return df

# Fonction pour mettre à jour une connaissance
def update_knowledge(entry_id, category, subcategory, title, content, image_path=None, modified_by="Anonymous"):
    c.execute("UPDATE knowledge SET category = ?, subcategory = ?, title = ?, content = ?, image_path = ?, last_modified_by = ? WHERE id = ?",
              (category, subcategory, title, content, image_path, modified_by, entry_id))
    conn.commit()

# Fonction pour supprimer une connaissance
def delete_knowledge(entry_id):
    c.execute("DELETE FROM knowledge WHERE id = ?", (entry_id,))
    conn.commit()

# Fonction pour exporter les données en CSV
def export_data():
    df = get_knowledge()
    export_path = "knowledge_export.csv"
    df.to_csv(export_path, index=False)
    return export_path

# Fonction pour importer les données depuis un CSV
def import_data(file_path):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        add_knowledge(row['category'], row['subcategory'], row['title'], row['content'], row.get('image_path'), row.get('created_by', "Anonymous"))

# Icônes pour les catégories
CATEGORY_ICONS = {
    "Linux": "🐧",
    "Wireshark": "🦈",
    "Nmap": "🌐",
    "Metasploit": "💀",
    "Markdown": "📝",
    "Autre": "🗂️"
}

# Interface Streamlit
st.title("🛜 CyberNotes")

# Saisir le nom de l'utilisateur
current_user = st.sidebar.text_input("Votre nom", value="Anonymous")

# Gestion des importations et exportations
if st.sidebar.button("Exporter les données en CSV"):
    export_path = export_data()
    st.sidebar.success(f"Données exportées avec succès : {export_path}")
    with open(export_path, "rb") as file:
        st.sidebar.download_button(
            label="Télécharger le fichier CSV",
            data=file,
            file_name="knowledge_export.csv",
            mime="text/csv"
        )

uploaded_file = st.sidebar.file_uploader("Importer un fichier CSV", type=["csv"])
if uploaded_file is not None:
    try:
        import_data(uploaded_file)
        st.sidebar.success("Données importées avec succès !")
    except Exception as e:
        st.sidebar.error(f"Erreur lors de l'importation : {e}")

# Formulaire d'ajout ou de modification de connaissance
option = st.sidebar.radio("Action", ["Ajouter", "Modifier", "Supprimer"])

if option == "Ajouter":
    category = st.sidebar.selectbox("Catégorie", list(CATEGORY_ICONS.keys()))

    # Récupérer les sous-catégories existantes pour la catégorie sélectionnée
    existing_data = get_knowledge()
    existing_subcategories = existing_data[existing_data['category'] == category]['subcategory'].dropna().unique()

    subcategory = st.sidebar.selectbox(
        "Sous-catégorie (ou ajouter une nouvelle)",
        ["Créer une nouvelle"] + list(existing_subcategories)
    )

    if subcategory == "Créer une nouvelle":
        subcategory = st.sidebar.text_input("Nouvelle sous-catégorie")

    title = st.sidebar.text_input("Titre de la connaissance")
    content = st.sidebar.text_area("Description / Commande (en Markdown)")
    uploaded_image = st.sidebar.file_uploader("Ajouter une image (optionnel)", type=["png", "jpg", "jpeg"])

    if st.sidebar.button("Ajouter"):
        image_path = None
        if uploaded_image:
            image_dir = "images"
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, uploaded_image.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
        
        add_knowledge(category, subcategory, title, content, image_path, created_by=current_user)
        st.sidebar.success("Ajout réussi !")

elif option == "Modifier":
    data = get_knowledge()
    if not data.empty:
        entry_title_map = {row['title']: row['id'] for _, row in data.iterrows()}
        entry_title = st.sidebar.selectbox("Sélectionner une entrée à modifier", list(entry_title_map.keys()))
        entry_id = entry_title_map[entry_title]
        entry = data[data['id'] == entry_id].iloc[0]
        
        category = st.sidebar.selectbox("Catégorie", list(CATEGORY_ICONS.keys()), index=list(CATEGORY_ICONS.keys()).index(entry['category']))

        existing_subcategories = data[data['category'] == category]['subcategory'].dropna().unique()
        subcategory = st.sidebar.selectbox(
            "Sous-catégorie (ou ajouter une nouvelle)",
            ["Créer une nouvelle"] + list(existing_subcategories),
            index=(["Créer une nouvelle"] + list(existing_subcategories)).index(entry['subcategory']) if entry['subcategory'] else 0
        )

        if subcategory == "Créer une nouvelle":
            subcategory = st.sidebar.text_input("Nouvelle sous-catégorie")

        title = st.sidebar.text_input("Titre de la connaissance", entry['title'])
        content = st.sidebar.text_area("Description / Commande (en Markdown)", entry['content'])
        uploaded_image = st.sidebar.file_uploader("Ajouter une nouvelle image (optionnel)", type=["png", "jpg", "jpeg"])

        if st.sidebar.button("Modifier"):
            image_path = entry['image_path']
            if uploaded_image:
                image_dir = "images"
                os.makedirs(image_dir, exist_ok=True)
                image_path = os.path.join(image_dir, uploaded_image.name)
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
            
            update_knowledge(entry_id, category, subcategory, title, content, image_path, modified_by=current_user)
            st.sidebar.success("Modification réussie !")

elif option == "Supprimer":
    data = get_knowledge()
    if not data.empty:
        entry_title_map = {row['title']: row['id'] for _, row in data.iterrows()}
        entry_title = st.sidebar.selectbox("Sélectionner une entrée à supprimer", list(entry_title_map.keys()))
        entry_id = entry_title_map[entry_title]

        if st.sidebar.button("Supprimer"):
            delete_knowledge(entry_id)
            st.sidebar.success("Suppression réussie !")

# Affichage des connaissances par chapitre et sous-catégorie
st.header("📂 Base de connaissances")
data = get_knowledge()
if not data.empty:
    search_query = st.text_input("🔍 Rechercher une connaissance")
    if search_query:
        data = data[data['title'].str.contains(search_query, case=False, na=False) | data['content'].str.contains(search_query, case=False, na=False)]

    categories = data['category'].unique()
    selected_category = st.selectbox("Choisir une catégorie", [f"{CATEGORY_ICONS[cat]} {cat}" for cat in categories])
    selected_category = selected_category.split(" ", 1)[1]  # Récupère uniquement le nom
    filtered_data = data[data['category'] == selected_category]

    subcategories = filtered_data['subcategory'].dropna().unique()
    subcategories = list(set(subcategories))  # Supprime les doublons
    if len(subcategories) > 0:
        selected_subcategory = st.selectbox("Choisir une sous-catégorie", ["Toutes"] + subcategories)
        if selected_subcategory != "Toutes":
            filtered_data = filtered_data[filtered_data['subcategory'] == selected_subcategory]

    if not filtered_data.empty:
        for _, row in filtered_data.iterrows():
            with st.expander(f"{CATEGORY_ICONS[row['category']]} {row['title']}"):
                st.markdown(f"**Créé par** : {row['created_by']}  ")
                st.markdown(f"**Dernière modification par** : {row['last_modified_by']}  ")
                st.markdown(row['content'])  # Utilisation de Markdown pour afficher la description
                if row['image_path'] and os.path.exists(row['image_path']):
                    st.image(row['image_path'], caption=row['title'])
    else:
        st.info("Aucune connaissance dans cette catégorie/sous-catégorie.")
else:
    st.info("Aucune connaissance enregistrée.")

# Fermeture de la connexion à la base de données
conn.close()
