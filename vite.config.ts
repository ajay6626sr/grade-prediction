import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// ✅ CHANGE THIS to your actual GitHub repo name!
export default defineConfig({
  plugins: [react()],
  base: '/grade-prediction/', // Example: '/grade-prediction/'
  build: {
    outDir: 'dist',
  },
});
