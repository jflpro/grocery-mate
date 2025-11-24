<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed, onMounted } from 'vue';

const authStore = useAuthStore();

const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.user);

const handleLogout = () => {
  authStore.logout();
};

onMounted(() => {
  authStore.initializeAuth();
});
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-green-600 p-4 text-white flex justify-between items-center shadow-md">
      <div class="flex gap-6">
        <!-- Dashboard doit pointer vers /app (app authentifiée), pas la landing / -->
        <router-link
          v-if="isAuthenticated"
          to="/app"
          class="hover:underline"
        >
          Dashboard
        </router-link>
        <router-link
          v-if="isAuthenticated"
          to="/ingredients"
          class="hover:underline"
        >
          Ingredients
        </router-link>
        <router-link
          v-if="isAuthenticated"
          to="/recipes"
          class="hover:underline"
        >
          Recipes
        </router-link>
        <router-link
          v-if="isAuthenticated"
          to="/shopping-lists"
          class="hover:underline"
        >
          Shopping Lists
        </router-link>

        <!-- Liens admin : visibles seulement si l'utilisateur est admin -->
        <router-link
          v-if="isAuthenticated && currentUser?.is_admin"
          to="/admin/users"
          class="hover:underline"
        >
          Admin
        </router-link>
        <router-link
          v-if="isAuthenticated && currentUser?.is_admin"
          to="/admin/landing"
          class="hover:underline"
        >
          Landing CMS
        </router-link>
      </div>

      <div class="flex items-center space-x-4">
        <template v-if="isAuthenticated">
          <span class="text-sm font-medium">
            Hi, <span class="font-bold">{{ currentUser?.username || 'User' }}</span>
          </span>
          <button
            @click="handleLogout"
            class="px-3 py-1 bg-red-500 hover:bg-red-700 rounded-lg text-sm font-semibold transition duration-150 ease-in-out shadow-md"
          >
            Log Out
          </button>
        </template>
        <template v-else>
          <router-link
            to="/login"
            class="px-3 py-1 hover:bg-green-700 rounded-lg text-sm font-semibold"
          >
            Login
          </router-link>
          <router-link
            to="/register"
            class="px-3 py-1 bg-green-500 hover:bg-green-400 rounded-lg text-sm font-semibold"
          >
            Register
          </router-link>
        </template>
      </div>
    </nav>

    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
body {
  font-family: Arial, sans-serif;
}
.router-link-exact-active {
  font-weight: bold;
  text-decoration: underline;
}
</style>
