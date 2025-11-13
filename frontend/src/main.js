import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { useAuthStore } from './stores/auth'

// --- Création de l’application Vue ---
const app = createApp(App)

// --- Configuration de Pinia et du Router ---
const pinia = createPinia()
app.use(pinia)
app.use(router)

// --- Vérification de la configuration d’environnement ---
console.group("🌍 Configuration environnement frontend")
console.log("VITE_BACKEND_URL =", import.meta.env.VITE_BACKEND_URL)
if (!import.meta.env.VITE_BACKEND_URL) {
  console.warn("⚠️ Attention : la variable VITE_BACKEND_URL est absente ou non chargée.")
  console.warn("Vérifie ton fichier frontend/.env et le docker-compose du service frontend.")
}
console.groupEnd()

// --- Initialisation de l’authentification ---
const authStore = useAuthStore()
try {
  await authStore.initializeAuth()
  console.log("✅ Authentification initialisée avec succès")
} catch (error) {
  console.error("❌ Erreur d’initialisation du store d’authentification :", error)
}

// --- Montage final ---
app.mount('#app')
console.log("🚀 Application Vue montée avec succès")
