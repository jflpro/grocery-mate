import { defineStore } from 'pinia';
import api, { authAPI } from '@/services/api';
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
        // 1. Obtenir le token (avec form-data)
        const tokenResponse = await api.post('/auth/token', new URLSearchParams(credentials), {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        });

        const token = tokenResponse.data.access_token;
        localStorage.setItem('access_token', token);

        // 2. Récupère les infos utilisateur (utilise l'intercepteur configuré dans api.js)
        await this.fetchUser();

        // 3. COMMANDE CRITIQUE DE REDIRECTION (vers la route nommée 'home')
        router.push({ name: 'home' });

        return true;
      } catch (error) {
        // Si la connexion ou le fetchUser échoue, forcer la déconnexion
        this.forceLogout(false);
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
            // Redirection vers la page de connexion après inscription réussie
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
        console.error("Échec de la récupération des informations utilisateur. Déconnexion forcée.", error);
        // Si fetchUser échoue (token invalide/expiré), on force la déconnexion
        this.forceLogout(false);
        throw error;
      }
    },

    /**
     * Logique de déconnexion principale (appelle l'API puis supprime l'état local).
     */
    async logout() {
        try {
            // 1. Appel au backend /logout pour tracer l'événement.
            await authAPI.logout(); 
        } catch (error) {
            console.warn("Échec de l'appel /logout, mais déconnexion locale effectuée.", error);
        } finally {
            // 2. Suppression locale des données et redirection.
            this.forceLogout();
        }
    },

    /**
     * Déconnecte l'utilisateur localement sans interaction API (utilisé en cas d'erreur de token).
     */
    forceLogout(shouldRedirect = true) {
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
