import { defineStore } from "pinia";
import api, { authAPI } from "@/services/api";
import router from "@/router";

export const useAuthStore = defineStore("auth", {
  // --- State ---
  state: () => ({
    user: null,                 // { id, email, username } or null
    isCheckingAuth: true,       // initial auth check in progress
    hasToken: !!localStorage.getItem("access_token"), // reactive flag
  }),

  // --- Getters ---
  getters: {
    // ✅ Authenticated if we have a token flag in the store
    isAuthenticated: (state) => state.hasToken,

    // Return current token (still read from localStorage)
    getToken: (state) =>
      state.hasToken ? localStorage.getItem("access_token") : null,

    currentUser: (state) => state.user,
  },

  // --- Actions ---
  actions: {
    // --- Login ---
    async login({ username, password, redirectPath = null }) {
      try {
        const formData = new URLSearchParams();
        formData.append("username", username); // backend expects "username"
        formData.append("password", password);

        const tokenResponse = await api.post("/auth/token", formData, {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });

        const token = tokenResponse.data.access_token;
        if (!token) throw new Error("Missing access token");

        // 1️⃣ Save token + update reactive flag
        localStorage.setItem("access_token", token);
        this.hasToken = true;

        // 2️⃣ Load user profile (optional but recommended)
        try {
          await this.fetchUser();
        } catch (e) {
          console.warn("Login: token OK but fetchUser failed", e);
          // Keep user logged in; UI can handle missing profile if needed.
        }

        // 3️⃣ Redirect to target (home by default)
        const target = redirectPath || { name: "home" };
        router.push(target);

        return true;
      } catch (error) {
        this.forceLogout(false);
        console.error("Login error:", error);
        throw error;
      }
    },

    // --- Register ---
    async register(data) {
      try {
        await authAPI.register(data);
        router.push({ name: "login" });
        return true;
      } catch (error) {
        console.error("Registration error:", error);
        throw error;
      }
    },

    // --- Fetch current user ---
    async fetchUser() {
      const token = this.getToken;
      if (!token) {
        this.user = null;
        this.hasToken = false;
        return;
      }

      try {
        const response = await authAPI.me();
        this.user = response.data;
      } catch (error) {
        console.error("Failed to fetch user. Forcing logout.", error);
        this.forceLogout(false);
        throw error;
      }
    },

    // --- Logout (API + local) ---
    async logout() {
      try {
        await authAPI.logout();
      } catch (error) {
        console.warn(
          "Logout API call failed, but performing local logout.",
          error,
        );
      } finally {
        this.forceLogout();
      }
    },

    // --- Local forced logout ---
    forceLogout(shouldRedirect = true) {
      localStorage.removeItem("access_token");
      this.hasToken = false;
      this.user = null;

      if (shouldRedirect) {
        router.push({ name: "login" });
      }
    },

    // --- Initialization on app start ---
    async initializeAuth() {
      this.isCheckingAuth = true;

      // Sync flag with localStorage at startup
      this.hasToken = !!localStorage.getItem("access_token");

      if (this.hasToken) {
        try {
          await this.fetchUser();
        } catch (e) {
          console.warn("initializeAuth: fetchUser failed", e);
        }
      }

      this.isCheckingAuth = false;
    },
  },
});
