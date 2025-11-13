// --- Vite Configuration pour GroceryMate Frontend ---
// Gère le serveur de développement, le proxy vers FastAPI,
// et la résolution des chemins d’imports Vue.

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],

  resolve: {
    alias: {
      // Permet d’utiliser @/ au lieu de chemins relatifs longs
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  server: {
    // --- Configuration du serveur de dev ---
    host: '0.0.0.0',  // Écoute sur toutes les interfaces (Docker-friendly)
    port: 5173,

    // --- Sécurité et compatibilité ---
    allowedHosts: [
      '.grocery-mate.work.gd', // Domaine du projet
      'localhost',
      '127.0.0.1',
      '0.0.0.0',
    ],

    // --- Proxy pour rediriger les appels /api vers le backend FastAPI ---
    proxy: {
      '/api': {
        // 🔧 L’URL du backend est lue depuis .env (ou fallback local)
        target: process.env.VITE_BACKEND_URL || 'http://grocery_backend:8000',
        changeOrigin: true,
        rewrite: (path) => path,
      },
    },
  },

  // --- Build de production corrigé ---
  build: {
    target: 'esnext',  // ✅ Autorise le top-level await
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined, // optimisation facultative
      },
    },
  },
})
