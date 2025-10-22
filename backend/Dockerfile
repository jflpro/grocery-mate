# Utilise une image Python légère et stable
FROM python:3.11-slim

# Met en place des variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Définit le répertoire de travail dans le conteneur
WORKDIR /app

# Copie le fichier de dépendances et installe-les
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le reste du code de l'application
COPY . .

# Commande de démarrage pour Django
CMD ["/bin/bash", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
