import { defineStore } from 'pinia';
// Correction du chemin: l'alias '@/services/api' pointe vers 'frontend/src/services/api.js'
import api, { authAPI } from '@/services/api';
// L'alias '@/router' pointe vers 'frontend/src/router/index.js'
import router from '@/router';

// Définition du Pinia Store pour l'authentification
export const useAuthStore = defineStore('auth', {
  // --- État (State) ---
  state: () => ({
    // Objet utilisateur : { id, email, username } ou null
    user: null,
    // Indique si l'application vérifie l'état d'authentification initial
    isCheckingAuth: true,
  }),

  // --- Getters ---
  getters: {
    // Vérifie si l'utilisateur est connecté (présence de l'objet user ET du token dans localStorage)
    isAuthenticated: (state) => !!state.user && !!localStorage.getItem('access_token'),
    // Retourne le jeton d'accès stocké
    getToken: () => localStorage.getItem('access_token'),
  },

  // --- Actions ---
  actions: {
    /**
     * Tente de connecter l'utilisateur.
     * @param {Object} credentials - { username, password }
     */
    async login(credentials) {
      try {
        // La route login (/auth/token) est gérée ici car elle requiert un format form-data
        // qui n'est pas le format par défaut de l'instance 'api' (JSON).
        const tokenResponse = await api.post('/auth/token', new URLSearchParams(credentials), {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });

        const token = tokenResponse.data.access_token;
        localStorage.setItem('access_token', token);

        // Après avoir reçu le jeton, on récupère les infos utilisateur
        await this.fetchUser();

        router.push({ name: 'home' });

        return true;
      } catch (error) {
        this.logout(false);
        throw error;
      }
    },

    /**
     * Tente d'inscrire un nouvel utilisateur en utilisant authAPI.
     * @param {Object} data - { email, username, password }
     */
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

    /**
     * Récupère les informations de l'utilisateur via /auth/me en utilisant authAPI.
     */
    async fetchUser() {
      if (!this.getToken) {
        this.user = null;
        return;
      }

      try {
        const response = await authAPI.me();
        this.user = response.data;
      } catch (error) {
        console.error("Échec de la récupération des informations utilisateur. Déconnexion.", error);
        this.logout(false);
      }
    },

    /**
     * Déconnecte l'utilisateur.
     */
    logout(shouldRedirect = true) {
      localStorage.removeItem('access_token');
      this.user = null;
      if (shouldRedirect) {
        router.push({ name: 'login' });
      }
    },

    /**
     * Initialise l'état d'authentification au démarrage de l'application.
     */
    async initializeAuth() {
        this.isCheckingAuth = true;
        if (this.getToken) {
            await this.fetchUser();
        }
        this.isCheckingAuth = false;
    }
  },
});
// L'initialisation est désormais gérée uniquement dans main.js.
