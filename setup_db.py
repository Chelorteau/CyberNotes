import sqlite3

conn = sqlite3.connect("cybernotes.db")
c = conn.cursor()

# Création ou mise à jour de la table knowledge
c.execute('''CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    subcategory TEXT,
    title TEXT,
    content TEXT,
    image_path TEXT,
    created_by TEXT,
    last_modified_by TEXT,
    tool TEXT,
    linked_to_note_id INTEGER DEFAULT NULL
)''')

# Création propre de la table deleted_knowledge si besoin
c.execute("DROP TABLE IF EXISTS deleted_knowledge")
c.execute('''CREATE TABLE deleted_knowledge (
    id INTEGER PRIMARY KEY,
    category TEXT,
    subcategory TEXT,
    title TEXT,
    content TEXT,
    image_path TEXT,
    created_by TEXT,
    last_modified_by TEXT,
    tool TEXT,
    linked_to_note_id INTEGER
)''')

conn.commit()
conn.close()

print("✅ La base de données est prête.")
