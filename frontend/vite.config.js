import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: "/ai-researcher/",
  server: {
    port: 3003,      
    strictPort: true 
  }

})

