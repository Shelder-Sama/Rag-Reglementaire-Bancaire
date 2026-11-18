import os
import datetime
import duckdb
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from google import genai
from fastapi import FastAPI
from pydantic import BaseModel

# Chargement des variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client_gemini = genai.Client(api_key=api_key)

# Initialisation de l'API
app = FastAPI(
    title="API RAG - Réglementation Bancaire BCE",
    description="Moteur de recherche sémantique basé sur Gemini et ChromaDB."
)

# On définit le format que l'API attend
class RequeteUtilisateur(BaseModel):
    question: str

# Création de la "porte d'entrée" /ask
@app.post("/ask")
def poser_question_api(requete: RequeteUtilisateur):
    question_posee = requete.question
    
    # 1. Recherche Vectorielle (ChromaDB)
    client_chroma = chromadb.PersistentClient(path="./data/chroma")
    modele_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client_chroma.get_collection(name="reglementation", embedding_function=modele_embeddings)
    
    resultats = collection.query(query_texts=[question_posee], n_results=3)
    contexte = "\n\n---\n\n".join(resultats['documents'][0])
    
    # 2. Prompt pour l'IA
    prompt = f"""Tu es un expert en réglementation bancaire européenne (BCE/EBA). 
    Réponds UNIQUEMENT via le contexte ci-dessous.
    
    Contexte : {contexte}
    Question : {question_posee}
    """
    
    # 3. Interrogation de Gemini avec Try/Except
    try:
        reponse = client_gemini.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        texte_final = reponse.text
        statut = "succès"
    except Exception as e:
        texte_final = "Erreur API : Les serveurs de Google sont actuellement indisponibles (503)."
        statut = "erreur"
    
    # 4. Traçabilité (DuckDB)
    connexion = duckdb.connect("./data/historique.duckdb")
    # On ajoute la table si elle n'existe pas
    connexion.execute("""
        CREATE TABLE IF NOT EXISTS logs_requetes (
            date_requete TIMESTAMP,
            question TEXT,
            reponse TEXT
        )
    """)
    connexion.execute(
        "INSERT INTO logs_requetes (date_requete, question, reponse) VALUES (?, ?, ?)", 
        (datetime.datetime.now(), question_posee, texte_final)
    )
    connexion.close()
    
    # 5. La réponse que l'API renvoie à l'utilisateur
    return {
        "question": question_posee,
        "reponse": texte_final,
        "statut": statut
    }