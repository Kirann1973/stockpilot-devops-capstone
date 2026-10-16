import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// In dev, `npm run dev` proxies /api to a backend on localhost:8000.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { '/api': 'http://localhost:8000' } },
});
