import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

import Dashboard from '@/views/Dashboard.vue';
import Ingredients from '@/views/Ingredients.vue';
import Recipes from '@/views/Recipes.vue';
import ShoppingLists from '@/views/ShoppingLists.vue';
import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';

// Admin views
import UserManagement from '@/views/admin/UserManagement.vue';

const routes = [
  {
    path: '/',
    name: 'home',
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
    path: '/shopping-lists',
    name: 'shopping-lists',
    component: ShoppingLists,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: UserManagement,
    meta: {
      requiresAuth: true,
      // Admin check is enforced by backend (403 if not admin)
    },
  },
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

// --- Global async guard ---
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  // Initial auth check
  if (authStore.isCheckingAuth) {
    await authStore.initializeAuth();
  }

  const isAuthenticated = authStore.isAuthenticated;
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const guestOnly = to.matched.some((record) => record.meta.guestOnly);

  // Protected routes
  if (requiresAuth && !isAuthenticated) {
    console.log('🔒 Redirection vers Login: Route protégée.');
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  // Guest-only routes
  if (guestOnly && isAuthenticated) {
    console.log('✅ Redirection vers Home: Déjà connecté.');
    next({ name: 'home' });
    return;
  }

  next();
});

export default router;
