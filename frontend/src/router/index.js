import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth'; // Importation de votre store Pinia
import Dashboard from '@/views/Dashboard.vue';
import Ingredients from '@/views/Ingredients.vue';
import Recipes from '@/views/Recipes.vue';
import ShoppingLists from '@/views/ShoppingLists.vue';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';

// Définition des routes
const routes = [
    {
        path: '/',
        name: 'home', // Renommé 'home' pour correspondre à la redirection dans le store
        component: Dashboard,
        meta: { requiresAuth: true } // Protégé
    },
    {
        path: '/ingredients',
        name: 'ingredients',
        component: Ingredients,
        meta: { requiresAuth: true } // Protégé
    },
    {
        path: '/recipes',
        name: 'recipes',
        component: Recipes,
        meta: { requiresAuth: true } // Protégé
    },
    {
        path: '/shopping-lists',
        name: 'shopping-lists',
        component: ShoppingLists,
        meta: { requiresAuth: true } // Protégé
    },
    {
        path: '/login',
        name: 'login',
        component: Login,
        meta: { guestOnly: true } // Seulement accessible si déconnecté
    },
    {
        path: '/register',
        name: 'register',
        component: Register,
        meta: { guestOnly: true } // Seulement accessible si déconnecté
    }
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes
});

// --- GARDE DE NAVIGATION GLOBAL ET ASYNCHRONE ---
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore();
    
    // Si la vérification initiale n'a pas été lancée ou est en cours (utile pour les reloads)
    if (authStore.user === null && authStore.getToken && authStore.isCheckingAuth) {
        // Lancer ou attendre la fin de la vérification asynchrone (fetchUser)
        await authStore.initializeAuth(); 
        // Note: L'appel au store au début du beforeEach garantit que l'état est à jour.
    }
    
    // Maintenant, l'état d'authentification est connu.
    const isAuthenticated = authStore.isAuthenticated;
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const guestOnly = to.matched.some(record => record.meta.guestOnly);

    // 1. Gérer les routes protégées
    if (requiresAuth && !isAuthenticated) {
        // Si la route nécessite l'authentification et l'utilisateur n'est pas connecté
        console.log("🔒 Redirection vers Login: Route protégée.");
        next({ name: 'login', query: { redirect: to.fullPath } });
        return;
    }

    // 2. Gérer les routes "invité seulement"
    if (guestOnly && isAuthenticated) {
        // Si l'utilisateur est connecté et essaie d'accéder à /login ou /register
        console.log("✅ Redirection vers Home: Déjà connecté.");
        next({ name: 'home' }); 
        return;
    }

    // 3. Continuer la navigation
    next();
});
// --- FIN DU GARDE DE NAVIGATION GLOBAL ---

export default router;
