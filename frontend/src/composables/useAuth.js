import { ref } from 'vue';

// État partagé et réactif
// Utiliser un pattern Singleton : l'état est créé une seule fois, 
// et toutes les instances de useAuth l'utilisent.
const isAuthenticated = ref(!!localStorage.getItem('token'));
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'));

/**
 * Simule la connexion de l'utilisateur.
 * @param {string} email - L'email de l'utilisateur.
 * @param {string} password - Le mot de passe de l'utilisateur.
 */
async function login(email, password) {
    // Simulation d'un appel API.
    console.log(`Tentative de connexion pour: ${email}`);
    
    // Simuler un échec
    if (email !== 'test@example.com' || password !== 'password') {
        throw new Error("Email ou mot de passe incorrect.");
    }

    // Simuler une réponse réussie
    const token = 'fake-vue3-token-12345';
    const userData = { email: email, name: 'Jean Dupont' };
    
    // Persistance et mise à jour de l'état
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));

    isAuthenticated.value = true;
    user.value = userData;

    return userData;
}

/**
 * Déconnecte l'utilisateur.
 */
function logout() {
    // Nettoyage et mise à jour de l'état
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    isAuthenticated.value = false;
    user.value = null;
}

/**
 * Composable qui expose les fonctions et l'état d'authentification.
 */
export function useAuth() {
    return {
        isAuthenticated,
        user,
        login,
        logout,
    };
}
