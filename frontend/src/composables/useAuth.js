// frontend/src/composables/useAuth.js
import { ref } from 'vue';
import { authAPI } from '@/services/api.js';

// 🌟 État partagé et réactif
const isAuthenticated = ref(!!localStorage.getItem('access_token'));
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));

/**
 * Connexion de l'utilisateur via l'API FastAPI
 * @param {string} email - Email de l'utilisateur
 * @param {string} password - Mot de passe de l'utilisateur
 */
async function login(email, password) {
    try {
        // 🔑 Obtenir le token JWT depuis /auth/token
        const response = await authAPI.login({ username: email, password });
        const token = response.data.access_token;

        // Stocker le token dans localStorage
        localStorage.setItem('access_token', token);

        // 🧍 Récupérer les infos de l'utilisateur depuis /auth/me
        const me = await authAPI.me();
        user.value = me.data;
        localStorage.setItem('user', JSON.stringify(me.data));

        isAuthenticated.value = true;

        return me.data;
    } catch (error) {
        // Renvoyer le message d'erreur du backend si présent
        throw new Error(error.response?.data?.detail || 'Erreur de connexion');
    }
}

/**
 * Déconnexion de l'utilisateur
 */
async function logout() {
    try {
        // Appel optionnel à /auth/logout côté backend
        await authAPI.logout();
    } catch (error) {
        console.warn("Erreur lors de la déconnexion côté backend:", error);
    }

    // Nettoyage côté frontend
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    isAuthenticated.value = false;
    user.value = null;
}

/**
 * Initialisation de l'état d'authentification au chargement
 * Permet de rester connecté si token présent dans localStorage
 */
async function initializeAuth() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
        // Vérifier que le token est valide et récupérer l'utilisateur
        const me = await authAPI.me();
        user.value = me.data;
        isAuthenticated.value = true;
    } catch (error) {
        // Token invalide -> nettoyage
        console.warn("Token invalide ou expiré, nettoyage localStorage");
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        isAuthenticated.value = false;
        user.value = null;
    }
}

/**
 * Composable exporté pour utilisation dans les composants
 */
export function useAuth() {
    return {
        isAuthenticated,
        user,
        login,
        logout,
        initializeAuth,
    };
}
