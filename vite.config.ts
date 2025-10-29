
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/grade-prediction/', // 👈 This line fixes 404s on GitHub Pages
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
})
