import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Le front tourne sur son propre serveur (port 5173), le back sur le sien
// (port 8000). Le proxy fait passer tout ce qui commence par /api vers le back :
// pour le navigateur, tout vient de la même origine, donc pas de CORS à régler.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
