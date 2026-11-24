# 1. Image de base légère avec Python
FROM python:3.10-slim

# 2. Définition du dossier de travail dans le conteneur
WORKDIR /app

# 3. Copie des dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copie de tout le code et des données (incluant ton dossier /data)
COPY . .

# 5. On expose le port 8000 pour que le Cloud puisse communiquer avec FastAPI
EXPOSE 8000

# 6. Commande de démarrage de l'API
CMD ["uvicorn", "5_api:app", "--host", "0.0.0.0", "--port", "8080"]