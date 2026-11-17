import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from google import genai

# 1. Charger la clé secrète depuis le fichier .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def poser_question(question):
    print(f"\n❓ Question : {question}")
    
    # 2. Se connecter à la base vectorielle ChromaDB
    print("🔍 Recherche dans les documents réglementaires...")
    client_chroma = chromadb.PersistentClient(path="./data/chroma")
    modele_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client_chroma.get_collection(name="reglementation", embedding_function=modele_embeddings)
    
    # 3. Trouver les 3 passages les plus pertinents par rapport à la question
    resultats = collection.query(
        query_texts=[question],
        n_results=3
    )
    
    passages = resultats['documents'][0]
    contexte = "\n\n---\n\n".join(passages)
    
    # 4. Préparer les instructions strictes pour l'IA (Prompt)
    prompt = f"""Tu es un expert en réglementation bancaire européenne (BCE/EBA). 
    Réponds à la question en te basant UNIQUEMENT sur le contexte fourni ci-dessous. 
    Si la réponse n'est pas dans le contexte, dis simplement que tu ne sais pas.
    Fais une réponse claire, synthétique et en français.
    
    Contexte extrait des documents officiels :
    {contexte}
    
    Question de l'utilisateur : {question}
    """
    
    # 5. Envoyer le tout à Google Gemini
    print("🤖 Rédaction de la réponse par Gemini...")
    client_gemini = genai.Client(api_key=api_key)
    reponse = client_gemini.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )
    
    print("\n✅ RÉPONSE FINALE :")
    print(reponse.text)
    print("\n" + "="*50)

if __name__ == "__main__":
    # J'ai mis une question liée au crédit puisque ton document s'appelle "creditunderwriting"
    ma_question = "Quels sont les principaux portefeuilles concernés par cet exercice de credit underwriting ?"
    poser_question(ma_question)