import axios from "axios";

// 🌐 URL de base du backend
// On prend d'abord l'URL du .env (VITE_BACKEND_URL), sinon fallback dev
const API_BASE = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000/api";

// --- Instance Axios principale ---
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// --- Intercepteur pour ajouter le token à chaque requête ---
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;

// --- Shopping Lists API ---
export const shoppingListsAPI = {
  getAll: () => api.get(`/shopping-lists/`),
  add: (data) => api.post(`/shopping-lists/`, data),
  update: (id, data) => api.put(`/shopping-lists/${id}`, data),
  delete: (id) => api.delete(`/shopping-lists/${id}`),
  addItem: (listId, item) => api.post(`/shopping-lists/${listId}/items`, item),
  updateItem: (itemId, data) => api.put(`/shopping-lists/items/${itemId}`, data),
  deleteItem: (itemId) => api.delete(`/shopping-lists/items/${itemId}`),
};

// --- Ingredients API ---
export const ingredientsAPI = {
  getAll: () => api.get(`/ingredients/`),
  add: (data) => api.post(`/ingredients/`, data),
  update: (id, data) => api.put(`/ingredients/${id}`, data),
  delete: (id) => api.delete(`/ingredients/${id}`),
  getExpiringSoon: () => api.get(`/ingredients/expiring/soon`),
  seedSample: () => api.post(`/ingredients/seed-sample`),
};

// --- Recipes API ---
export const recipesAPI = {
  getAll: () => api.get(`/recipes/`),
  add: (data) => api.post(`/recipes/`, data),
  update: (id, data) => api.put(`/recipes/${id}`, data),
  delete: (id) => api.delete(`/recipes/${id}`),
  findMatching: () => api.get(`/recipes/match/ingredients`),
  seedSample: () => api.post(`/recipes/seed-sample`),
};

// --- Auth API ---
export const authAPI = {
  register: (data) => api.post(`/auth/register`, data),

  // Login avec OAuth2 password (x-www-form-urlencoded)
  login: (email, password) => {
    const formData = new URLSearchParams();
    formData.append("username", email); // backend attend email dans "username"
    formData.append("password", password);

    return api.post(`/auth/token`, formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  me: () => api.get(`/auth/me`),
  logout: () => api.post(`/auth/logout`),
};

// --- Seed global (données de test) ---
export const seedAPI = {
  seedAll: () => api.post(`/seed/`),
};
