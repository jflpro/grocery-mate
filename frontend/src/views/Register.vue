<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const authStore = useAuthStore();

// Form fields
const email = ref('');
const username = ref('');
const password = ref('');
const passwordConfirm = ref('');

// UI state
const isLoading = ref(false);
const error = ref(null);

/**
 * Handle registration form submission.
 */
const handleRegister = async () => {
    isLoading.value = true;
    error.value = null;

    if (password.value !== passwordConfirm.value) {
        error.value = "Passwords do not match.";
        isLoading.value = false;
        return;
    }
    
    // For the API, we send { email, username, password }
    const credentials = {
        email: email.value,
        username: username.value,
        password: password.value
    };

    try {
        await authStore.register(credentials);
        
        // The store already handles redirection to 'login' on success,
        // but we could show a success message here if we wanted to stay
        // on the same page (not the case here, the store redirects).
        
    } catch (err) {
        // The store rejects the error, we catch it here to display to the user
        let errorMessage = "Registration failed.";
        
        // Try to extract a more specific error message from the API response (FastAPI/Axios)
        if (err.response && err.response.data && err.response.data.detail) {
            errorMessage = typeof err.response.data.detail === 'string' 
                           ? err.response.data.detail 
                           : "Please check the form data.";
        } else {
             // If the error is a standard Error object
             errorMessage = err.message || errorMessage;
        }

        error.value = errorMessage;
        console.error("Registration error caught:", err);

    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-50 p-4">
    <div class="w-full max-w-md bg-white p-8 rounded-xl shadow-2xl border border-gray-100">

      <h2 class="text-3xl font-extrabold text-center text-indigo-700 mb-6">
        Create Account
      </h2>

      <form @submit.prevent="handleRegister" class="space-y-6">
        <!-- Email field -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
          <div class="mt-1">
            <input
              id="email"
              name="email"
              type="email"
              v-model="email"
              required
              autocomplete="email"
              class="appearance-none block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out sm:text-sm"
              placeholder="your.email@example.com"
            />
          </div>
        </div>
        
        <!-- Username field -->
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700">Username</label>
          <div class="mt-1">
            <input
              id="username"
              name="username"
              type="text"
              v-model="username"
              required
              autocomplete="username"
              class="appearance-none block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 transition duration-150 ease-in-out sm:text-sm"
              placeholder="your_username"
            />
          </div>
        </div>

        <!-- Password field -->
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
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

        <!-- Password confirmation field -->
        <div>
          <label for="password-confirm" class="block text-sm font-medium text-gray-700">Confirm Password</label>
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

        <!-- Error message (if any) -->
        <p v-if="error" class="text-sm font-medium text-red-600 text-center bg-red-50 p-2 rounded-lg border border-red-200">
          {{ error }}
        </p>

        <!-- Register button -->
        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out disabled:opacity-50"
          >
            <span v-if="isLoading">Registering...</span>
            <span v-else>Create Account</span>
          </button>
        </div>
      </form>

      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Already have an account?
          <router-link :to="{ name: 'login' }" class="font-medium text-indigo-600 hover:text-indigo-500">
            Log In
          </router-link>
        </p>
      </div>

    </div>
  </div>
</template>
