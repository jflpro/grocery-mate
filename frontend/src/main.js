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

// Utilisation des middlewares
app.use(pinia);
app.use(router);

// --- Initialisation de l'authentification ---
// Doit être fait après 'app.use(pinia)'
// On crée l'instance du store pour pouvoir appeler l'action d'initialisation
const authStore = useAuthStore();
authStore.initializeAuth(); 

// Montage de l'application
app.mount('#app');
