import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image

# Création de la base de données
DB_PATH = "cybernotes.db"
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Fonctions

def add_knowledge(category, subcategory, title, content, image_path=None, created_by="Anonymous", tool="", linked_to=None):
    subcategory = subcategory.strip().capitalize() if subcategory else ""
    c.execute("""INSERT INTO knowledge (category, subcategory, title, content, image_path, created_by, last_modified_by, tool, linked_to_note_id)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (category, subcategory, title, content, image_path, created_by, created_by, tool, linked_to))
    conn.commit()

def get_knowledge():
    return pd.read_sql_query("SELECT * FROM knowledge", conn)

def get_deleted_knowledge():
    return pd.read_sql_query("SELECT * FROM deleted_knowledge", conn)

def update_knowledge(entry_id, category, subcategory, title, content, image_path=None, modified_by="Anonymous", tool="", linked_to=None):
    subcategory = subcategory.strip().capitalize() if subcategory else ""
    c.execute("""UPDATE knowledge SET category = ?, subcategory = ?, title = ?, content = ?, image_path = ?,
              last_modified_by = ?, tool = ?, linked_to_note_id = ? WHERE id = ?""",
              (category, subcategory, title, content, image_path, modified_by, tool, linked_to, entry_id))
    conn.commit()

def delete_knowledge(entry_id):
    row = c.execute("SELECT * FROM knowledge WHERE id = ?", (entry_id,)).fetchone()
    if row:
        c.execute("INSERT INTO deleted_knowledge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
        c.execute("DELETE FROM knowledge WHERE id = ?", (entry_id,))
        conn.commit()

def restore_knowledge(entry_id):
    row = c.execute("SELECT * FROM deleted_knowledge WHERE id = ?", (entry_id,)).fetchone()
    if row:
        c.execute("INSERT INTO knowledge VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
        c.execute("DELETE FROM deleted_knowledge WHERE id = ?", (entry_id,))
        conn.commit()

def permanently_delete(entry_id):
    c.execute("DELETE FROM deleted_knowledge WHERE id = ?", (entry_id,))
    conn.commit()

def export_data():
    df = get_knowledge()
    path = "knowledge_export.csv"
    df.to_csv(path, index=False)
    return path

def import_data(file_path):
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        add_knowledge(row['category'], row['subcategory'], row['title'], row['content'], row.get('image_path'), row.get('created_by', "Anonymous"), row.get('tool', ""))

CATEGORY_ICONS = {
    "Linux": "🐧",
    "Wireshark": "🦈",
    "Metasploit": "💀",
    "Markdown": "📝",
    "Réseau": "📶",
    "PenTest": "🔐",
    "Autre": "🗂️"
}

data = get_knowledge()

st.set_page_config(page_title="CyberNote", layout="wide")
st.title("🛜 CyberNotes")
current_user = st.sidebar.text_input("Votre nom", value="Anonymous")

# Formulaire d'ajout
with st.sidebar.expander("➕ Ajouter une nouvelle connaissance"):
    category = st.selectbox("Catégorie", list(CATEGORY_ICONS.keys()), key="add_category")
    existing_data = get_knowledge()
    existing_subcategories = existing_data[existing_data['category'] == category]['subcategory'].dropna().unique()
    cleaned_subcategories = sorted(set([s.strip().capitalize() for s in existing_subcategories if s]))
    subcategory = st.selectbox("Sous-catégorie (ou nouvelle)", ["Créer une nouvelle"] + cleaned_subcategories, key="add_subcat_select")
    if subcategory == "Créer une nouvelle":
        subcategory = st.text_input("Nouvelle sous-catégorie", key="add_subcat_text")
    title = st.text_input("Titre", key="add_title")
    tool = st.text_input("Outil utilisé (facultatif)", key="add_tool")

    format_type = st.selectbox("Format du contenu", ["Markdown", "LaTeX"], key="add_format")
    if format_type == "Markdown":
        content = st.text_area("Contenu (Markdown)", key="add_content")
    else:
        content = st.text_area("Contenu (LaTeX)", key="add_content")

    uploaded_image = st.file_uploader("Image (optionnelle)", type=["png", "jpg", "jpeg"], key="add_img")

    if st.button("Ajouter", key="add_btn"):
        image_path = None
        if uploaded_image:
            image_dir = "images"
            os.makedirs(image_dir, exist_ok=True)
            image_path = os.path.join(image_dir, uploaded_image.name)
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
        add_knowledge(category, subcategory, title, content, image_path, created_by=current_user, tool=tool)
        st.success("Ajout effectué !")


# Formulaire de création de raccourcis
with st.sidebar.expander("🔗 Créer un raccourci vers une note existante"):
    shortcut_category = st.selectbox("Catégorie du raccourci", list(CATEGORY_ICONS.keys()), key="shortcut_category")
    shortcut_subcategory = st.text_input("Sous-catégorie du raccourci", key="shortcut_subcat")
    shortcut_title = st.text_input("Titre du raccourci", key="shortcut_title")

    existing_notes = data[data['linked_to_note_id'].isna()]  # filtre uniquement les vraies notes
    note_choices = [f"{r['subcategory']} - {r['title']} (id={r['id']})" for _, r in existing_notes.iterrows()]
    shortcut_target = st.selectbox("Note cible", note_choices, key="shortcut_target")

    if st.button("Créer le raccourci", key="create_shortcut_btn"):
        target_id = int(shortcut_target.split("id=")[-1].strip(")"))
        add_knowledge(
            shortcut_category,
            shortcut_subcategory,
            shortcut_title,
            content="",
            image_path=None,
            created_by=current_user,
            tool="",
            linked_to=target_id
        )
        st.success("Raccourci créé avec succès !")
        st.rerun()


# Affichage des connaissances
st.header("📂 Base de connaissances")
if not data.empty:
    if st.button("🔄 Recharger l'interface"):
        st.rerun()

    search_query = st.text_input("🔍 Rechercher par mot-clé ou outil")
    if search_query:
        data = data[data.apply(lambda row: search_query.lower() in str(row['title']).lower() or
                                           search_query.lower() in str(row['content']).lower() or
                                           search_query.lower() in str(row['tool']).lower(), axis=1)]

    categories = sorted(set(data['category'].dropna()))
    displayable_categories = [cat for cat in categories if cat in CATEGORY_ICONS]

    if displayable_categories:
        selected_display = st.selectbox("Catégorie", [f"{CATEGORY_ICONS[cat]} {cat}" for cat in displayable_categories])
        selected_category = selected_display.split(" ", 1)[1]
        filtered_data = data[data['category'] == selected_category]

        subcategories = sorted(set([s.strip().capitalize() for s in filtered_data['subcategory'].dropna()]))
        if subcategories:
            selected_subcat = st.selectbox("Sous-catégorie", ["Toutes"] + subcategories)
            if selected_subcat != "Toutes":
                filtered_data = filtered_data[filtered_data['subcategory'].str.strip().str.capitalize() == selected_subcat]

            for _, row in filtered_data.iterrows():
                is_shortcut = False
                if pd.notnull(row['linked_to_note_id']):
                    shortcut_target = data[data['id'] == row['linked_to_note_id']]
                    if not shortcut_target.empty:
                        shortcut_row = shortcut_target.iloc[0]
                        st.markdown(f"🔗 **Raccourci vers : `{shortcut_row['category']} > {shortcut_row['subcategory']}`**")
                        st.markdown(f"**Titre cible :** {shortcut_row['title']}")
                        is_shortcut = True

                with st.expander(f"{CATEGORY_ICONS.get(row['category'], '')} {row['title']}"):
                    st.markdown(f"**Créé par :** {row['created_by']}")
                    st.markdown(f"**Modifié par :** {row['last_modified_by']}")
                    if row['tool']:
                        st.markdown(f"**Outil utilisé :** `{row['tool']}`")
                    if "$" in row['content']:
                        st.latex(row['content'])
                    else:
                        st.markdown(row['content'])

                    if row['image_path'] and os.path.exists(row['image_path']):
                        st.image(row['image_path'], caption=row['title'])

                    if not is_shortcut and st.checkbox("✏️ Modifier", key=f"edit_{row['id']}"):
                        new_title = st.text_input("Titre", row['title'], key=f"title_{row['id']}")
                        new_content = st.text_area("Contenu", row['content'], key=f"content_{row['id']}")
                        new_category = st.selectbox("Catégorie", list(CATEGORY_ICONS.keys()), index=list(CATEGORY_ICONS.keys()).index(row['category']), key=f"cat_{row['id']}")
                        new_subcategory = st.text_input("Sous-catégorie", row['subcategory'] or "", key=f"subcat_{row['id']}")
                        new_tool = st.text_input("Outil utilisé", row['tool'] or "", key=f"tool_{row['id']}")

                        all_notes = data[(data['id'] != row['id']) & (data['subcategory'].notna())]
                        all_notes_display = [f"{r['subcategory']} - {r['title']} (id={r['id']})" for _, r in all_notes.iterrows()]
                        selected_link = st.selectbox("Raccourci vers une autre sous-catégorie (optionnel)", ["Aucun"] + all_notes_display, key=f"link_{row['id']}")
                        linked_id = None
                        if selected_link != "Aucun":
                            linked_id = int(selected_link.split("id=")[-1].strip(")"))

                        new_img = st.file_uploader("Nouvelle image", type=["png", "jpg", "jpeg"], key=f"img_{row['id']}")
                        if st.button("Enregistrer", key=f"save_{row['id']}"):
                            image_path = row['image_path']
                            if new_img:
                                image_dir = "images"
                                os.makedirs(image_dir, exist_ok=True)
                                image_path = os.path.join(image_dir, new_img.name)
                                with open(image_path, "wb") as f:
                                    f.write(new_img.getbuffer())
                            update_knowledge(row['id'], new_category, new_subcategory, new_title, new_content, image_path, modified_by=current_user, tool=new_tool, linked_to=linked_id)
                            st.success("Modifié avec succès !")
                            st.rerun()

                    # Boutons de suppression
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🗑️ Supprimer", key=f"delete_{row['id']}"):
                            delete_knowledge(row['id'])
                            st.success("Note déplacée dans la corbeille.")
                            st.rerun()
                    with col2:
                        if is_shortcut:
                            if st.button("🧹 Supprimer uniquement le raccourci", key=f"unlink_{row['id']}"):
                                update_knowledge(row['id'], row['category'], row['subcategory'], row['title'], row['content'],
                                                row['image_path'], modified_by=current_user, tool=row['tool'], linked_to=None)
                                st.success("Raccourci supprimé.")
                                st.rerun()

else:
    st.info("Aucune donnée disponible.")


# Corbeille
st.header("🗃️ Corbeille")
deleted = get_deleted_knowledge()
if not deleted.empty:
    for _, row in deleted.iterrows():
        with st.expander(f"🗑️ {row['title']}"):
            st.markdown(f"**Créé par :** {row['created_by']}")
            st.markdown(f"**Modifié par :** {row['last_modified_by']}")
            if row['tool']:
                st.markdown(f"**Outil utilisé :** `{row['tool']}`")
            if "$" in row['content']:
                st.latex(row['content'])
            else:
                st.markdown(row['content'])
            if row['image_path'] and os.path.exists(row['image_path']):
                st.image(row['image_path'], caption=row['title'])

            col1, col2 = st.columns(2)
            if col1.button("♻️ Restaurer", key=f"restore_{row['id']}"):
                restore_knowledge(row['id'])
                st.success("Note restaurée !")
                st.rerun()
            if col2.button("❌ Supprimer définitivement", key=f"permadelete_{row['id']}"):
                permanently_delete(row['id'])
                st.success("Note supprimée définitivement.")
                st.rerun()
else:
    st.info("Aucune note supprimée.")

conn.close()