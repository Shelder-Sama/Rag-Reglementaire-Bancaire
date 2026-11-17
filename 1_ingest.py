import os
from pypdf import PdfReader

def decouper_texte(texte, taille_chunk=1000, chevauchement=200):
    """Découpe le texte en morceaux en gardant un chevauchement pour le contexte."""
    chunks = []
    debut = 0
    while debut < len(texte):
        fin = debut + taille_chunk
        chunks.append(texte[debut:fin])
        debut += taille_chunk - chevauchement
    return chunks

def traiter_pdfs(dossier="data"):
    tous_les_chunks = []
    if not os.path.exists(dossier):
        print(f"Erreur: Le dossier '{dossier}' n'existe pas.")
        return []

    for fichier in os.listdir(dossier):
        if fichier.endswith('.pdf'):
            chemin = os.path.join(dossier, fichier)
            reader = PdfReader(chemin)
            texte_complet = ""
            
            for page in reader.pages:
                extrait = page.extract_text()
                if extrait:
                    texte_complet += extrait + "\n"
            
            morceaux = decouper_texte(texte_complet)
            print(f"✅ {fichier} : {len(morceaux)} passages générés.")
            tous_les_chunks.extend(morceaux)
    return tous_les_chunks

if __name__ == "__main__":
    print("Démarrage de la lecture des PDF...")
    chunks = traiter_pdfs()
    if len(chunks) > 0:
        print(f"🎉 Objectif réussi ! Total : {len(chunks)} morceaux de texte extraits.")