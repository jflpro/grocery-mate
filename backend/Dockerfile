# ------------------------------------------------------------
# 📁 backend/Dockerfile
# 🎯 Dockerfile pour FastAPI + Uvicorn
# ------------------------------------------------------------

# Utilise une image Python légère et stable
FROM python:3.11-slim

# Variables d'environnement Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier requirements et installe les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste du code
COPY . .

# Commande de démarrage FastAPI avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
