import api from "./api";

export const aiAPI = {
  ask: (question) => api.get("/ai/ask", { params: { question } }),
  recipe: (ingredients) => api.get("/ai/recipe", { params: { ingredients } }),
};
