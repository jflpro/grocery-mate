# ------------------------------------------------------------
# 📁 backend/Dockerfile
# 🎯 Dockerfile pour FastAPI + Uvicorn en production
# ------------------------------------------------------------

FROM python:3.11-slim

# Empêche Python de générer des fichiers .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Répertoire de travail
WORKDIR /app

# Installation de dépendances système nécessaires pour argon2-cffi
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code backend
COPY . .

# Démarre FastAPI/Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
