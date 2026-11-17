import os
import datetime
import duckdb
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def poser_question(question):
    print(f"\n❓ Question : {question}")
    
    print("🔍 Recherche dans les documents réglementaires...")
    client_chroma = chromadb.PersistentClient(path="./data/chroma")
    modele_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client_chroma.get_collection(name="reglementation", embedding_function=modele_embeddings)
    
    resultats = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    contexte = "\n\n---\n\n".join(resultats['documents'][0])
    
    prompt = f"""Tu es un expert en réglementation bancaire européenne (BCE/EBA). 
    Réponds à la question en te basant UNIQUEMENT sur le contexte fourni ci-dessous. 
    Si la réponse n'est pas dans le contexte, dis simplement que tu ne sais pas.
    Fais une réponse claire, synthétique et en français.
    
    Contexte extrait des documents officiels :
    {contexte}
    
    Question de l'utilisateur : {question}
    """
    
    print("🤖 Rédaction de la réponse par Gemini...")
    client_gemini = genai.Client(api_key=api_key)
    
    try:
        # On essaie d'appeler l'API
        reponse = client_gemini.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        texte_final = reponse.text
    except Exception as e:
        # Si Google plante, on rattrape l'erreur proprement sans crasher
        texte_final = "Erreur API : Les serveurs de Google sont actuellement indisponibles (503)."
        
    print("\n✅ RÉPONSE FINALE :")
    print(texte_final)
    print("\n" + "="*50)
    
    # --- Traçabilité SQL ---
    print("💾 Enregistrement de la requête dans la base de données...")
    connexion = duckdb.connect("./data/historique.duckdb")
    connexion.execute("""
        CREATE TABLE IF NOT EXISTS logs_requetes (
            date_requete TIMESTAMP,
            question TEXT,
            reponse TEXT
        )
    """)
    connexion.execute(
        "INSERT INTO logs_requetes (date_requete, question, reponse) VALUES (?, ?, ?)", 
        (datetime.datetime.now(), question, texte_final)
    )
    connexion.close()
    print("✅ Enregistrement terminé.")

if __name__ == "__main__":
    ma_question = "Quels sont les principaux portefeuilles concernés par cet exercice de credit underwriting ?"
    poser_question(ma_question)