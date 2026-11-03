import { defineConfig, devices } from '@playwright/test'
import { BASE_E2E, carpetaBackend, python } from './e2e/semilla.js'

// Un solo comando: "pnpm test:e2e --headed" levanta el backend y el frontend de prueba,
// siembra la base budget_e2e y corre las pruebas. Usa puertos propios (8099 y 5199)
// para no chocar con la app que tengas abierta (8000 y 5173; un segundo "pnpm dev" toma 5174).
const API = 'http://localhost:8099'
const APP = 'http://localhost:5199'

export default defineConfig({
  testDir: './e2e',
  globalSetup: './e2e/semilla.js',
  timeout: 30_000,
  retries: 0,
  // Una prueba a la vez: todas comparten la misma base de datos
  workers: 1,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    baseURL: APP,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'escritorio',
      use: {
        ...devices['Desktop Chrome'],
        // E2E_CHANNEL=msedge usa el Edge instalado en vez del Chromium de Playwright
        ...(process.env.E2E_CHANNEL ? { channel: process.env.E2E_CHANNEL } : {}),
      },
    },
  ],
  webServer: [
    {
      command: `"${python}" -m uvicorn app.main:app --port 8099`,
      cwd: carpetaBackend,
      // SMTP_HOST vacio: el enlace de recuperacion sale en la consola, nunca se envia un correo real
      env: { DATABASE_NAME: BASE_E2E, CORS_ORIGINS: APP, FRONTEND_URL: APP, SMTP_HOST: '' },
      url: `${API}/api/health`,
      // Nunca reutilizar: otro servidor en ese puerto podria usar otra base de datos
      reuseExistingServer: false,
    },
    {
      command: 'pnpm exec vite --port 5199 --strictPort',
      env: { API_PROXY: API },
      url: APP,
      reuseExistingServer: false,
    },
  ],
})
