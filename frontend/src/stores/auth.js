import { defineStore } from 'pinia';
import api, { authAPI } from '@/services/api';
import router from '@/router';

// Définition du Pinia Store pour l'authentification
export const useAuthStore = defineStore('auth', {
  // --- État (State) ---
  state: () => ({
    user: null,           // Objet utilisateur : { id, email, username } ou null
    isCheckingAuth: true, // Indique si l'application vérifie l'état d'authentification initial
  }),

  // --- Getters ---
  getters: {
    // Vérifie si l'utilisateur est connecté
    isAuthenticated: (state) => !!state.user && !!localStorage.getItem('access_token'),
    
    // Retourne le token pour être utilisable comme this.getToken()
    getToken: (state) => () => localStorage.getItem('access_token'),
  },

  // --- Actions ---
  actions: {
    // --- Connexion ---
    async login({ username, password, redirectPath = null }) { 
      try {
        const formData = new URLSearchParams();
        formData.append("username", username); // backend attend "username"
        formData.append("password", password);

        const tokenResponse = await api.post('/auth/token', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        const token = tokenResponse.data.access_token;
        if (!token) throw new Error("Token manquant");
        localStorage.setItem('access_token', token);

        // Récupérer les infos utilisateur après stockage du token
        await this.fetchUser();

        // Redirection vers la page initialement demandée ou home
        const target = redirectPath || { name: 'home' };
        router.push(target);

        return true;

      } catch (error) {
        this.forceLogout(false);
        console.error("Erreur login:", error);
        throw error;
      }
    },

    // --- Inscription ---
    async register(data) {
      try {
        await authAPI.register(data);
        router.push({ name: 'login' });
        return true;
      } catch (error) {
        console.error("Erreur d'inscription:", error);
        throw error;
      }
    },

    // --- Récupération utilisateur ---
    async fetchUser() {
      if (!this.getToken()) {  // appeler le getter
        this.user = null;
        return;
      }

      try {
        const response = await authAPI.me();
        this.user = response.data;
      } catch (error) {
        console.error("Échec récupération utilisateur. Déconnexion forcée.", error);
        this.forceLogout(false);
        throw error;
      }
    },

    // --- Déconnexion ---
    async logout() {
      try {
        await authAPI.logout(); 
      } catch (error) {
        console.warn("Échec de l'appel /logout, mais déconnexion locale effectuée.", error);
      } finally {
        this.forceLogout();
      }
    },

    // --- Déconnexion forcée locale ---
    forceLogout(shouldRedirect = true) {
      localStorage.removeItem('access_token');
      this.user = null;
      if (shouldRedirect) {
        router.push({ name: 'login' });
      }
    },

    // --- Initialisation du store au démarrage ---
    async initializeAuth() {
      this.isCheckingAuth = true;
      if (this.getToken()) {  // appeler le getter
        await this.fetchUser();
      }
      this.isCheckingAuth = false;
    }
  },
});
