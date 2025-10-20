import axios from "axios";

// 🌐 Récupération de l'URL de base du backend à partir des variables d'environnement.
// Si VITE_BACKEND_URL n'est pas défini (par exemple, en production), on peut fournir une valeur par défaut.
const API_BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000/api";

// 1. Création de l'instance Axios configurée
const api = axios.create({
  // Utilise l'URL récupérée depuis les variables d'environnement
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// 2. Intercepteur pour l'injection du jeton
// Cet intercepteur s'exécute avant chaque requête.
api.interceptors.request.use(
  (config) => {
    // Récupérer le token du localStorage
    const token = localStorage.getItem("access_token");

    // Si un token existe, on l'ajoute à l'en-tête Authorization.
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. Exportation de l'instance par défaut
// C'est cette instance que les vues d'authentification utiliseront.
export default api;

// 4. Utilisation de l'instance 'api' pour toutes les API de ressources

// 🛒 --- Shopping Lists API ---
export const shoppingListsAPI = {
  // Lire toutes les listes
  getAll: () => api.get(`/shopping-lists/`),

  // Créer une nouvelle liste
  add: (data) => api.post(`/shopping-lists/`, data),

  // Mettre à jour une liste (nom, etc.)
  update: (id, data) => api.put(`/shopping-lists/${id}`, data),

  // Supprimer une liste
  delete: (id) => api.delete(`/shopping-lists/${id}`),

  // Ajouter un item à une liste donnée
  addItem: (listId, item) => api.post(`/shopping-lists/${listId}/items`, item),

  // Mettre à jour un item existant
  updateItem: (itemId, data) => api.put(`/shopping-lists/items/${itemId}`, data),

  // Supprimer un item
  deleteItem: (itemId) => api.delete(`/shopping-lists/items/${itemId}`),
};

// 🍄 --- Ingredients API ---
export const ingredientsAPI = {
  getAll: () => api.get(`/ingredients/`),
  add: (data) => api.post(`/ingredients/`, data),
  update: (id, data) => api.put(`/ingredients/${id}`, data),
  delete: (id) => api.delete(`/ingredients/${id}`),

  // Ingrédients qui expirent bientôt
  getExpiringSoon: () => api.get(`/ingredients/expiring/soon`),

  // Remplir la base avec des données d’exemple
  seedSample: () => api.post(`/ingredients/seed-sample`),
};

// 🍽️ --- Recipes API ---
export const recipesAPI = {
  getAll: () => api.get(`/recipes/`),
  add: (data) => api.post(`/recipes/`, data),
  update: (id, data) => api.put(`/recipes/${id}`, data),
  delete: (id) => api.delete(`/recipes/${id}`),

  // Trouver les recettes réalisables avec les ingrédients disponibles
  findMatching: () => api.get(`/recipes/match/ingredients`),

  // Charger des recettes d’exemple
  seedSample: () => api.post(`/recipes/seed-sample`),
};

// 🔑 --- Auth API ---
// NOTE IMPORTANTE: Nous utilisons 'api' pour ces routes.
// L'intercepteur n'ajoute pas le token si la requête n'en a pas encore, ce qui est correct pour login/register.
export const authAPI = {
  register: (data) => api.post(`/auth/register`, data),
  // La route /auth/token (login) utilise un format form-data, nous l'appellerons directement depuis Login.vue
  me: () => api.get(`/auth/me`),
};

// 🧪 --- Seed global (toutes les données de test) ---
export const seedAPI = {
  seedAll: () => api.post(`/seed/`),
};
