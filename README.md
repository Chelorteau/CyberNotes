# CyberNote 📖

CyberNote est une **application web interactive** développée avec **Streamlit** et **SQLite** pour organiser et gérer des connaissances en cybersécurité. Elle permet d'ajouter, modifier, supprimer et rechercher des informations sous forme de chapitres et sous-catégories. 

## 🌟 **Fonctionnalités principales**

✅ **Ajout, modification et suppression de connaissances**
✅ **Organisation par catégories et sous-catégories**
✅ **Support des images et format Markdown**
✅ **Moteur de recherche intégré**
✅ **Exportation et importation des données au format CSV**
✅ **Fonctionnalités collaboratives : suivi du créateur et dernier modificateur**

---

## 🚀 **Installation et exécution locale**

### **1️⃣ Prérequis**
- Python 3.7+
- Git
- Pip (ou conda)

### **2️⃣ Cloner le projet**
```sh
 git clone https://github.com/Chelorteau/CyberNotes
 cd cybernote
```

### **3️⃣ Installer les dépendances**
```sh
pip install -r requirements.txt
```

### **4️⃣ Lancer l'application**
```sh
streamlit run main.py
```

L'application sera accessible à l'adresse **http://localhost:8501**

---

## 🔧 **Configuration de la base de données**
CyberNote utilise SQLite pour stocker les connaissances. Au premier lancement, un fichier `cybernotes.db` sera automatiquement créé.

Si tu veux **réinitialiser** la base de données, supprime le fichier `cybernotes.db` :
```sh
rm cybernotes.db
```

---

## 📚 **Utilisation de CyberNote**

### **🔹 Ajouter une connaissance**
1. Sélectionner une **catégorie** (Linux, Wireshark, Nmap…)
2. Ajouter un **titre** et un **contenu** (Markdown pris en charge)
3. Optionnel : Ajouter une image 📷
4. Valider pour **ajouter à la base de connaissances** ✅

### **🔹 Rechercher une connaissance**
- Utiliser la **barre de recherche** pour retrouver rapidement une information.
- Filtrer par **catégorie** et **sous-catégorie**.

### **🔹 Modifier ou supprimer**
- Modifier une entrée en mettant à jour son titre, contenu ou image.
- Supprimer une connaissance si elle n’est plus pertinente.

---

## 📌 **Améliorations futures**
🚀 Intégration d’un **système de commentaires et annotations**  
🚀 Ajout d’une **authentification utilisateur** pour les contributions  
🚀 Support des **commandes Linux interactives** directement dans l’application  

---

## 🎯 **Contribuer au projet**
Tu veux contribuer ? Forke le projet et propose tes améliorations via des PRs !

📩 **Contact** : chelolorteau333@gmail.com
🔗 **GitHub** : https://github.com/Chelorteau/CyberNotes
🚀 **Happy Hacking & Stay Secure !** 🔒
