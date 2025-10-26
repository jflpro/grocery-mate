import { createApp } from 'vue';
// 1. Import du package Pinia
import { createPinia } from 'pinia'; 
import App from './App.vue';
import router from './router'; 
import './assets/main.css';
// 2. Import du store d'authentification
import { useAuthStore } from './stores/auth'; 

// Création de l'application Vue
const app = createApp(App);

// 3. Création de l'instance Pinia
const pinia = createPinia();
app.use(pinia);
app.use(router);

// --- TEST .env ---
console.log("VITE_BACKEND_URL:", import.meta.env.VITE_BACKEND_URL); 
// Si undefined -> ton fichier .env n'est pas détecté

// --- Initialisation de l'authentification ---
const authStore = useAuthStore();
authStore.initializeAuth(); 

// Montage de l'application
app.mount('#app');
