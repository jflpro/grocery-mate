<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const authStore = useAuthStore();

// Champs du formulaire
const email = ref('');
const username = ref('');
const password = ref('');
const passwordConfirm = ref('');

// État de l'interface
const isLoading = ref(false);
const error = ref(null);

/**
 * Gestionnaire de la soumission du formulaire d'inscription.
 */
const handleRegister = async () => {
    isLoading.value = true;
    error.value = null;

    if (password.value !== passwordConfirm.value) {
        error.value = "Les mots de passe ne correspondent pas.";
        isLoading.value = false;
        return;
    }
    
    // Pour l'API, nous envoyons { email, username, password }
    const credentials = {
        email: email.value,
        username: username.value,
        password: password.value
    };

    try {
        await authStore.register(credentials);
        
        // Le store gère déjà la redirection vers 'login' en cas de succès, 
        // mais nous affichons un message de succès ici si nous voulions rester
        // sur la même page (ce n'est pas le cas ici, le store redirige).
        
    } catch (err) {
        // Le store rejette l'erreur, nous la captons pour l'affichage utilisateur
        let errorMessage = "Échec de l'inscription.";
        
        // Tentative d'extraire un message d'erreur plus spécifique de la réponse de l'API (FastAPI/Axios)
        if (err.response && err.response.data && err.response.data.detail) {
            errorMessage = typeof err.response.data.detail === 'string' 
                           ? err.response.data.detail 
                           : "Vérifiez les données du formulaire.";
        } else {
             // Si l'erreur est un objet Error standard (ex: mot de passe non-correspondant)
             errorMessage = err.message || errorMessage;
        }

        error.value = errorMessage;
        console.error("Erreur d'inscription capturée:", err);

    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50 p-4">
    <div class="w-full max-w-md bg-white p-8 rounded-xl shadow-2xl border border-gray-100">

      <h2 class="text-3xl font-extrabold text-center text-indigo-700 mb-6">
        Créer un Compte
      </h2>

      <form @submit.prevent="handleRegister" class="space-y-6">
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
        
        <!-- Champ Nom d'utilisateur -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">Nom d'Utilisateur</label>
          <div class="mt-1">
            <input
              id="username"
              name="username"
              type="text"
              v-model="username"
              required
              autocomplete="username"
              class="appearance-none block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out sm:text-sm"
              placeholder="votre_nom"
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
              autocomplete="new-password"
              class="appearance-none block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out sm:text-sm"
              placeholder="••••••••"
            />
          </div>
        </div>

        <!-- Champ Confirmation Mot de passe -->
        <div>
          <label for="password-confirm" class="block text-sm font-medium text-gray-700">Confirmer le Mot de Passe</label>
          <div class="mt-1">
            <input
              id="password-confirm"
              name="password-confirm"
              type="password"
              v-model="passwordConfirm"
              required
              autocomplete="new-password"
              class="appearance-none block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out sm:text-sm"
              placeholder="••••••••"
            />
          </div>
        </div>

        <!-- Message d'erreur (si présent) -->
        <p v-if="error" class="text-sm font-medium text-red-600 text-center bg-red-50 p-2 rounded-lg border border-red-200">
          {{ error }}
        </p>

        <!-- Bouton d'inscription -->
        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out disabled:opacity-50"
          >
            <span v-if="isLoading">Inscription en cours...</span>
            <span v-else>Créer le Compte</span>
          </button>
        </div>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Déjà un compte ?
          <router-link :to="{ name: 'login' }" class="font-medium text-indigo-600 hover:text-indigo-500">
            Se connecter
          </router-link>
        </p>
      </div>

    </div>
  </div>
</template>
