# Étape 1 : Build de l'application
FROM node:18-slim AS builder

# Installation de dépendances nécessaires pour build (facultatif mais utile)
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et installation des dépendances
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Copie du reste du projet
COPY . .

# Build de production
RUN npm run build

# Étape 2 : Serveur Nginx pour servir le build
FROM nginx:alpine

# Supprime la config par défaut pour éviter les conflits
RUN rm /etc/nginx/conf.d/default.conf

# Copie du build généré
COPY --from=builder /app/dist /usr/share/nginx/html

# Copie d'une config Nginx optimisée pour SPA (Vue/React/Vite)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exposition du port standard
EXPOSE 80

# Lancement d’Nginx
CMD ["nginx", "-g", "daemon off;"]
