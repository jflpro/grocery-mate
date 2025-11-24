import axios from "axios";

// ---------------------------------------------------------------------------
// 🌐 Backend base URL (prod / dev)
// ---------------------------------------------------------------------------
//
// In prod : VITE_BACKEND_URL = https://api.gro-mate.tech
// In dev  : VITE_BACKEND_URL = http://localhost:8000 (in .env.local, for example)
const VITE_BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function normalizeBaseUrl(url) {
  if (!url) return url;
  return url.endsWith("/") ? url.slice(0, -1) : url;
}

let API_BASE = "";

// If env var is defined, use it
if (VITE_BACKEND_URL) {
  API_BASE = normalizeBaseUrl(VITE_BACKEND_URL) + "/api";
} else {
  // Fallback: relative /api path (same scheme as the page, so no Mixed Content)
  API_BASE = "/api";
}

console.log("🌍 Frontend environment configuration");
console.log("VITE_BACKEND_URL =", VITE_BACKEND_URL);
console.log("API_BASE =", API_BASE);

// --- Axios instance ---
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// --- JWT interceptor ---
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error),
);

export default api;

// ---------------------------------------------------------------------------
// 🤖 AI (Gemini)
// ---------------------------------------------------------------------------
export const aiAPI = {
  ask: (question) => api.get("/ai/ask", { params: { question } }),
  recipe: (ingredients) => api.get("/ai/recipe", { params: { ingredients } }),
};

// ---------------------------------------------------------------------------
// 🧺 Shopping Lists
//   Backend: /api/shopping-lists/ ...
// ---------------------------------------------------------------------------
export const shoppingListsAPI = {
  // Lists
  getAll: () => api.get("/shopping-lists/"), // GET  /shopping-lists/
  createList: (data) => api.post("/shopping-lists/", data), // POST /shopping-lists/  { name }

  // Items inside a given list
  addItem: (listId, data) =>
    api.post(`/shopping-lists/${listId}/items`, data), // POST /shopping-lists/{listId}/items

  updateItem: (itemId, data) =>
    api.put(`/shopping-lists/items/${itemId}`, data), // PUT  /shopping-lists/items/{itemId}

  deleteItem: (itemId) =>
    api.delete(`/shopping-lists/items/${itemId}`), // DELETE /shopping-lists/items/{itemId}
};

// ---------------------------------------------------------------------------
// 🥕 Ingredients
//   Backend: /api/ingredients/ ...
// ---------------------------------------------------------------------------
export const ingredientsAPI = {
  // NOTE: optional location param pour Dashboard (Fridge / Pantry)
  getAll: (location) =>
    api.get("/ingredients/", {
      params: location ? { location } : undefined,
    }),
  add: (data) => api.post("/ingredients/", data),
  update: (id, data) => api.put(`/ingredients/${id}`, data),
  delete: (id) => api.delete(`/ingredients/${id}`),

  getExpiringSoon: (days = 7) =>
    api.get("/ingredients/expiring/soon", { params: { days } }),

  seedSample: () => api.post("/ingredients/seed-sample"),
};

// ---------------------------------------------------------------------------
// 🍽 Recipes
//   Backend: /api/recipes/
// ---------------------------------------------------------------------------
export const recipesAPI = {
  getAll: () => api.get("/recipes/"),
  add: (data) => api.post("/recipes/", data),
  update: (id, data) => api.put(`/recipes/${id}`, data),
  delete: (id) => api.delete(`/recipes/${id}`),

  findMatching: () => api.get("/recipes/match/ingredients"),
  seedSample: () => api.post("/recipes/seed-sample"),
};

// ---------------------------------------------------------------------------
// 🔐 Auth
//   Backend: /api/auth/register, /api/auth/token, /api/auth/me, /api/auth/logout
// ---------------------------------------------------------------------------
export const authAPI = {
  register: (data) => api.post("/auth/register", data),

  login: (email, password) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    return api.post("/auth/token", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  me: () => api.get("/auth/me"),
  logout: () => api.post("/auth/logout"),
};

// ---------------------------------------------------------------------------
// 🌱 Seed (sample data)
//   Backend: POST /api/seed/
// ---------------------------------------------------------------------------
export const seedAPI = {
  seedAll: () => api.post("/seed/"),
};

// ---------------------------------------------------------------------------
// 🧱 Landing page (CMS)
//   Backend: /api/landing/public, /api/landing/admin
// ---------------------------------------------------------------------------
export const landingAPI = {
  // Public: contenu de la landing
  getPublic: () => api.get("/landing/public"),

  // Admin: lire le contenu actuel
  getAdmin: () => api.get("/landing/admin"),

  // Admin: mise à jour complète
  updateAdmin: (payload) => api.put("/landing/admin", payload),
};

// ---------------------------------------------------------------------------
// 📰 News (articles pour la landing)
//   Backend: /api/news/...
// ---------------------------------------------------------------------------
export const newsAPI = {
  // Public
  getPublic: (limit = 3) =>
    api.get("/news/public", { params: { limit } }),
  getBySlug: (slug) => api.get(`/news/public/${slug}`),

  // Admin
  listAdmin: (includeUnpublished = true) =>
    api.get("/news/", {
      params: { include_unpublished: includeUnpublished },
    }),
  create: (data) => api.post("/news/", data),
  update: (id, data) => api.put(`/news/${id}`, data),
  delete: (id) => api.delete(`/news/${id}`),
};
