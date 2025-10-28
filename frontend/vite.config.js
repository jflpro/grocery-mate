import { defineConfig } from 'vite' 
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    // Autorise les requêtes depuis ton domaine et tous les sous-domaines
    allowedHosts: ['.grooo-mate.work.gd'],
    proxy: {
      '/api': {
        target: 'http://95.91.21.21:8000', // <- ton backend
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
