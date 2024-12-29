import streamlit as st
import json
import spacy
from fuzzywuzzy import process

# Charger le modèle spaCy pour l'analyse des questions
try:
    nlp = spacy.load("fr_core_news_md")
except Exception as e:
    st.error(f"Erreur lors du chargement du modèle spaCy: {e}")
    nlp = None

# Configuration de la page
st.set_page_config(
    page_title="Chatbot Cacao",
    page_icon="🌱",
    layout="centered"
)

# CSS personnalisé pour l'interface
st.markdown("""
    <style>
    .main-title {
        color: #1E88E5;  /* Couleur bleue définie ici */
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-bottom: 2px solid #1E88E5;
        margin-bottom: 30px;
    }
    .stTextInput > div > div > input {
        border-radius: 15px;
    }
    .response-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin: 10px 0;
    }
    .confidence-box {
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 14px;
    }
    .high-confidence {
        background-color: #c8e6c9;
        color: #2e7d32;
    }
    .medium-confidence {
        background-color: #fff3e0;
        color: #f57c00;
    }
    .low-confidence {
        background-color: #ffebee;
        color: #c62828;
    }
    .akwaba-text {
        color: #2e7d32;  /* Couleur verte */
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    """Charge les données depuis un fichier JSON ou un dictionnaire."""
    try:
        with open('cocoa.json.txt', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Affichage du message en marron
            st.markdown('<p style="color:brown; font-size: 20px; text-align: center;">Faisons un voyage dans les bonnes pratiques en cacao culture !</p>', unsafe_allow_html=True)
            return data
    except FileNotFoundError:
        st.error("📁 Le fichier cocoa.json.txt n'a pas été trouvé.")
        return None
    except json.JSONDecodeError:
        st.error("⚠ Erreur de décodage du fichier JSON.")
        return None

def parse_questions(data):
    """Transforme les données de contenu et questions en un format lisible."""
    parsed_data = []
    for section in data['sections']:
        questions = section.get('questions', [])
        parsed_data.append({
            "section": section['section'],
            "content": section['content'],
            "questions": questions
        })
    return parsed_data

def get_best_match(query, questions):
    """Utilise Fuzzy matching pour trouver la meilleure correspondance parmi les questions."""
    results = process.extract(query, questions, limit=3)
    best_match, score = results[0]
    return best_match, score

def get_response(query, data):
    """Retourne une réponse basée sur la meilleure correspondance de la question."""
    parsed_data = parse_questions(data)
    query = query.lower()

    # Extraire les questions et utiliser fuzzy matching pour trouver la meilleure réponse
    all_questions = [q for section in parsed_data for q in section['questions']]
    best_match, similarity = get_best_match(query, all_questions)

    if similarity > 80:
        for section in parsed_data:
            if best_match in section['questions']:
                return section['content'], similarity
    return "Désolé, je n'ai pas trouvé de réponse spécifique à votre question.", 0.0

def display_confidence(similarity):
    """Affiche l'indice de confiance basé sur la similarité de la question."""
    if similarity > 0:
        if similarity >= 0.8:
            confidence_class = "high-confidence"
            emoji = "🟢"
        elif similarity >= 0.5:
            confidence_class = "medium-confidence"
            emoji = "🟡"
        else:
            confidence_class = "low-confidence"
            emoji = "🔴"
        
        st.markdown(f"""
            <div class="confidence-box {confidence_class}">
                {emoji} Indice de confiance: {similarity:.1%}
            </div>
        """, unsafe_allow_html=True)

def main():
    # Titre principal avec du HTML pour la couleur bleue
    st.markdown('<h1 class="main-title" style="color:#1E88E5;">🌱 Itinéraire Technique du Cacao</h1>', unsafe_allow_html=True)

    # Affichage du texte "AKWABA !" en vert
    st.markdown('<div class="akwaba-text">AKWABA !</div>', unsafe_allow_html=True)
    
    # Chargement des données
    data = load_data()
    if data is None:
        return
    
    # Zone de chat
    with st.container():
        question = st.text_input("💭 Posez une question sur l'itinéraire technique du cacao:", 
                               key="question_input",
                               placeholder="Exemple: Comment choisir les semences de cacao ?")
        
        if question:
            with st.spinner('Recherche de la meilleure réponse...'):
                response_content, similarity = get_response(question, data)
                
                if response_content:
                    st.markdown(f"""
                        <div class="response-box">
                            <strong>🤖 Stéphane:</strong><br>{response_content}
                        </div>
                    """, unsafe_allow_html=True)
                
                display_confidence(similarity)
        
        # Pied de page
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666;'>"
            "💡 Pour de meilleurs résultats, posez des questions précises et concises."
            "</div>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
