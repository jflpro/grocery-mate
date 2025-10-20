<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const isLoading = ref(false);
const error = ref(null);

/**
 * Gestionnaire de la soumission du formulaire de connexion.
 * Appelle la méthode login du store pour authentifier l'utilisateur.
 */
const handleLogin = async () => {
    isLoading.value = true;
    error.value = null;

    try {
        // L'action login du store utilise 'username' comme clé pour l'email
        await authStore.login({ 
            username: email.value, 
            password: password.value 
        });
        
        // Si le login est réussi, le store gère la redirection vers 'home'
        // Nous n'avons rien d'autre à faire ici.

    } catch (err) {
        // Capturer l'erreur pour l'afficher à l'utilisateur
        const errorMessage = err.response?.data?.detail || 'Erreur de connexion inconnue. Vérifiez vos identifiants.';
        error.value = errorMessage;
        console.error("Échec de la connexion (affichage utilisateur):", errorMessage);
        
        // S'assurer que la déconnexion a lieu en cas d'échec (même si le store le fait déjà)
        authStore.logout(false); 
    } finally {
        isLoading.value = false;
    }
};

</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50 p-4">
    <div class="w-full max-w-md bg-white p-8 rounded-xl shadow-2xl border border-gray-100">

      <h2 class="text-3xl font-extrabold text-center text-indigo-700 mb-6">
        Se Connecter
      </h2>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <!-- Champ Email -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Adresse Email</label>
          <div class="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              v-model="email"
              required
              autocomplete="email"
              class="appearance-none block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out sm:text-sm"
              placeholder="votre.email@exemple.com"
            />
          </div>
        </div>

        <!-- Champ Mot de passe -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">Mot de Passe</label>
          <div class="mt-1">
            <input
              id="password"
              name="password"
              type="password"
              v-model="password"
              required
              autocomplete="current-password"
              class="appearance-none block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out sm:text-sm"
              placeholder="••••••••"
            />
          </div>
        </div>

        <!-- Message d'erreur (si présent) -->
        <p v-if="error" class="text-sm font-medium text-red-600 text-center bg-red-50 p-2 rounded-lg border border-red-200">
          {{ error }}
        </p>

        <!-- Bouton de connexion -->
        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out disabled:opacity-50"
          >
            <span v-if="isLoading">Connexion en cours...</span>
            <span v-else>Se Connecter</span>
          </button>
        </div>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Pas encore de compte ?
          <router-link :to="{ name: 'register' }" class="font-medium text-indigo-600 hover:text-indigo-500">
            Créer un compte
          </router-link>
        </p>
      </div>

    </div>
  </div>
</template>
