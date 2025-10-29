import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// ✅ IMPORTANT: match your GitHub repo name here
export default defineConfig({
  plugins: [react()],
  base: '/grade-prediction/', // this MUST match your repo name
});
