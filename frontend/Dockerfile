# ------------------------------------------------------------
# Étape 1 : Build du frontend avec Node
# ------------------------------------------------------------
FROM node:18-slim AS builder

# Installation de dépendances système utiles
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

# Dossier de travail
WORKDIR /app

# Copie des fichiers package et installation des deps
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Copie de tout le projet
COPY . .

# Build de production Vite
RUN npm run build


# ------------------------------------------------------------
# Étape 2 : Serveur Nginx pour le build
# ------------------------------------------------------------
FROM nginx:alpine

# Nettoyage de la config par défaut
RUN rm /etc/nginx/conf.d/default.conf

# Copie du build dist/ dans nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copie la config nginx (doit contenir le fallback /index.html)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposer le port 80
EXPOSE 80

# Lancement de Nginx
CMD ["nginx", "-g", "daemon off;"]
