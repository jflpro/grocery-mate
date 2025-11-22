import { defineStore } from "pinia";
import api, { authAPI } from "@/services/api";
import router from "@/router";

// Définition du Pinia Store pour l'authentification
export const useAuthStore = defineStore("auth", {
  // --- État (State) ---
  state: () => ({
    user: null,           // Objet utilisateur : { id, email, username } ou null
    isCheckingAuth: true, // Indique si l'application vérifie l'état d'authentification initial
  }),

  // --- Getters ---
  getters: {
    // 🔧 FIX : connecté dès qu'un access_token existe
    isAuthenticated: () => !!localStorage.getItem("access_token"),

    // Retourne directement le token
    getToken: () => localStorage.getItem("access_token"),

    // Optionnel : accès direct au user
    currentUser: (state) => state.user,
  },

  // --- Actions ---
  actions: {
    // --- Connexion ---
    async login({ username, password, redirectPath = null }) {
      try {
        const formData = new URLSearchParams();
        formData.append("username", username); // backend attend "username"
        formData.append("password", password);

        const tokenResponse = await api.post("/auth/token", formData, {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });

        const token = tokenResponse.data.access_token;
        if (!token) throw new Error("Token manquant");

        // 1️⃣ On stocke le token → isAuthenticated devient true immédiatement
        localStorage.setItem("access_token", token);

        // 2️⃣ Puis on tente de charger le profil utilisateur
        try {
          await this.fetchUser();
        } catch (e) {
          console.warn("Login: token OK mais fetchUser a échoué", e);
          // On ne force pas le logout ici, on laisse l'utilisateur connecté
          // et éventuellement on gérera ça dans l'UI si besoin.
        }

        // 3️⃣ Redirection vers la page initialement demandée ou home
        const target = redirectPath || { name: "home" };
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
        router.push({ name: "login" });
        return true;
      } catch (error) {
        console.error("Erreur d'inscription:", error);
        throw error;
      }
    },

    // --- Récupération utilisateur ---
    async fetchUser() {
      const token = this.getToken; // getter = propriété
      if (!token) {
        this.user = null;
        return;
      }

      try {
        const response = await authAPI.me();
        this.user = response.data;
      } catch (error) {
        console.error(
          "Échec récupération utilisateur. Déconnexion forcée.",
          error,
        );
        this.forceLogout(false); // on ne redirige pas forcément, à toi de voir
        throw error;
      }
    },

    // --- Déconnexion ---
    async logout() {
      try {
        await authAPI.logout();
      } catch (error) {
        console.warn(
          "Échec de l'appel /logout, mais déconnexion locale effectuée.",
          error,
        );
      } finally {
        this.forceLogout();
      }
    },

    // --- Déconnexion forcée locale ---
    forceLogout(shouldRedirect = true) {
      localStorage.removeItem("access_token");
      this.user = null;
      if (shouldRedirect) {
        router.push({ name: "login" });
      }
    },

    // --- Initialisation du store au démarrage ---
    async initializeAuth() {
      this.isCheckingAuth = true;

      const token = this.getToken;
      if (token) {
        try {
          await this.fetchUser();
        } catch (e) {
          console.warn("initializeAuth: fetchUser a échoué", e);
        }
      }

      this.isCheckingAuth = false;
    },
  },
});
