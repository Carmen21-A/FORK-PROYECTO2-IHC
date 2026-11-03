import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 5173,
    // En desarrollo, /api se envia al backend FastAPI (las pruebas E2E usan otro puerto)
    proxy: { '/api': process.env.API_PROXY ?? 'http://localhost:8000' },
    // Los reportes de Playwright no son codigo: no vigilarlos
    watch: { ignored: ['**/playwright-report/**', '**/test-results/**'] },
  },
  test: {
    include: ['tests/unit/**/*.test.js'],
  },
})
