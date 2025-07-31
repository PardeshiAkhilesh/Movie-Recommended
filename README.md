# 🎬 Movie Recommender System

A simple yet stylish movie recommendation web app built with **Flask**, **Pandas**, and **OMDb API**. It recommends similar movies using **cosine similarity** and fetches movie posters dynamically.

---

## 🚀 Features

- 🔍 Search for any movie from the dataset
- 🤖 Recommends top 9 similar movies
- 🎨 Beautiful dark-themed UI inspired by Netflix
- 🖼️ Poster images fetched in real-time from the OMDb API
- 📜 Autocomplete suggestions using HTML `<datalist>`

---

## 🧠 How It Works

This is a **content-based recommender**:
- Movies and their metadata are processed offline.
- Cosine similarity is computed and saved in `similarity.pkl`.
- On user input, top similar movies are selected and displayed.

---

## 📦 Folder Structure

project-root/
│
├── app.py # Flask backend
├── Data/
│ ├── movies.pkl # Movie metadata
│ └── similarity.pkl # Precomputed cosine similarity matrix
│
├── templates/
│ └── index.html # Frontend HTML (with Bootstrap)
│
├── static/ (optional) # For CSS/images if needed
│
├── requirements.txt # Python dependencies
└── README.md # You're here!

## 🧑‍💻 Author
Akhilesh Pardeshi
Made with ❤️ and Flask