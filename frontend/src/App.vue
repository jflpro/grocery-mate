<script setup>
import { useAuthStore } from '@/stores/auth';
import { computed, onMounted } from 'vue'; // Ajout de 'onMounted' pour l'initialisation

// 1. Initialisation du store Pinia
const authStore = useAuthStore();

// 2. Utiliser un computed pour accéder facilement à l'état d'authentification
const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.user);

/**
 * Gère le clic sur le bouton de déconnexion.
 * Appelle l'action async 'logout' du store.
 */
const handleLogout = () => {
    // Cette action appelle l'API /logout puis supprime le token localement.
    authStore.logout();
};

// Initialise l'état d'authentification au chargement de l'application (pour rester connecté)
onMounted(() => {
    authStore.initializeAuth();
});
</script>

<template>
    <div class="min-h-screen bg-gray-50">
        <!-- Barre de navigation mise à jour pour inclure la logique de déconnexion -->
        <nav class="bg-green-600 p-4 text-white flex justify-between items-center shadow-md">
            
            <!-- Liens de navigation (alignés à gauche/centre) -->
            <div class="flex gap-6">
                <router-link to="/" class="hover:underline">Dashboard</router-link>
                <!-- Ces liens devraient idéalement utiliser v-if="isAuthenticated" pour être protégés -->
                <router-link to="/ingredients" class="hover:underline">Ingredients</router-link>
                <router-link to="/recipes" class="hover:underline">Recipes</router-link>
                <router-link to="/shopping-lists" class="hover:underline">Shopping Lists</router-link>
            </div>

            <!-- Boutons de connexion / Déconnexion (alignés à droite) -->
            <div class="flex items-center space-x-4">
                <template v-if="isAuthenticated">
                    <!-- Affichage de l'utilisateur connecté -->
                    <span class="text-sm font-medium">
                        Salut, <span class="font-bold">{{ currentUser?.username || 'Utilisateur' }}</span>
                    </span>

                    <!-- Le bouton de déconnexion -->
                    <button 
                        @click="handleLogout" 
                        class="px-3 py-1 bg-red-500 hover:bg-red-700 rounded-lg text-sm font-semibold transition duration-150 ease-in-out shadow-md"
                    >
                        Déconnexion
                    </button>
                </template>
                <template v-else>
                    <!-- Liens Connexion/Inscription si déconnecté -->
                    <router-link to="/login" class="px-3 py-1 hover:bg-green-700 rounded-lg text-sm font-semibold">
                        Connexion
                    </router-link>
                    <router-link to="/register" class="px-3 py-1 bg-green-500 hover:bg-green-400 rounded-lg text-sm font-semibold">
                        Inscription
                    </router-link>
                </template>
            </div>
        </nav>

        <main class="p-6">
            <router-view></router-view>
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
