import chromadb
from chromadb.utils import embedding_functions
import importlib

# On importe ton premier script pour récupérer les passages découpés
ingest = importlib.import_module("1_ingest")

def creer_base_vectorielle():
    print("1. Récupération des passages du PDF...")
    chunks = ingest.traiter_pdfs("data")
    
    if not chunks:
        print("Erreur : Aucun texte trouvé.")
        return

    print("2. Initialisation de ChromaDB...")
    client = chromadb.PersistentClient(path="./data/chroma")
    
    # Le modèle est déjà téléchargé sur ton PC maintenant !
    modele_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    print("3. Création de la collection 'reglementation'...")
    # CORRECTION : On attrape n'importe quelle erreur si la collection n'existe pas encore
    try:
        client.delete_collection(name="reglementation")
    except Exception:
        pass
        
    collection = client.create_collection(
        name="reglementation", 
        embedding_function=modele_embeddings
    )

    print(f"4. Calcul des vecteurs en cours (ça peut prendre 1 à 2 minutes pour {len(chunks)} passages)...")
    
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        ids=ids
    )
    
    print("🎉 Base vectorielle créée avec succès ! L'IA est prête à chercher des informations.")

if __name__ == "__main__":
    creer_base_vectorielle()