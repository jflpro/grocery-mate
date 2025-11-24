import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

// Public landing page
import LandingPage from '@/views/landing/LandingPage.vue';

// Authenticated views
import Dashboard from '@/views/Dashboard.vue';
import Ingredients from '@/views/Ingredients.vue';
import Recipes from '@/views/Recipes.vue';
import ShoppingLists from '@/views/ShoppingLists.vue';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';

// Admin views
import UserManagement from '@/views/admin/UserManagement.vue';
import LandingCms from '@/views/admin/LandingCms.vue';

const routes = [
  // Public landing page
  {
    path: '/',
    name: 'landing',
    component: LandingPage,
    meta: { requiresAuth: false },
  },

  // Authenticated app entry
  {
    path: '/app',
    name: 'home', // garder ce nom pour les redirections existantes
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/ingredients',
    name: 'ingredients',
    component: Ingredients,
    meta: { requiresAuth: true },
  },
  {
    path: '/recipes',
    name: 'recipes',
    component: Recipes,
    meta: { requiresAuth: true },
  },
  {
    // route cohérente avec le composant et les liens
    path: '/shopping-lists',
    name: 'shopping-lists',
    component: ShoppingLists,
    meta: { requiresAuth: true },
  },

  // Admin
  {
    path: '/admin/users',
    name: 'admin-users',
    component: UserManagement,
    meta: {
      requiresAuth: true,
      // Le backend renvoie 403 si l'utilisateur n'est pas admin
    },
  },
  {
    path: '/admin/landing',
    name: 'admin-landing',
    component: LandingCms,
    meta: {
      requiresAuth: true,
      // Backoffice CMS pour la landing
    },
  },

  // Auth
  {
    path: '/login',
    name: 'login',
    component: Login,
    meta: { guestOnly: true },
  },
  {
    path: '/register',
    name: 'register',
    component: Register,
    meta: { guestOnly: true },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// --- Global guard ---
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  const isAuthenticated = authStore.isAuthenticated;
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const guestOnly = to.matched.some((record) => record.meta.guestOnly);

  // Routes protégées
  if (requiresAuth && !isAuthenticated) {
    console.log('🔒 Redirection vers Login: route protégée.');
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  // Routes réservées aux invités (login / register)
  if (guestOnly && isAuthenticated) {
    console.log('✅ Redirection vers Home: déjà connecté.');
    next({ name: 'home' });
    return;
  }

  // La landing "/" reste accessible même connecté
  next();
});

export default router;
