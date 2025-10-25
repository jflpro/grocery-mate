# Utilise Node.js léger
FROM node:18-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier package.json et package-lock.json
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste du code
COPY . .

# Lancer le serveur Vite
CMD ["npm", "run", "dev"]
