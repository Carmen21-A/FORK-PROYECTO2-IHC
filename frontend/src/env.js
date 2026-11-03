// Reemplaza a lib/env.dart: las variables se leen de frontend/.env (prefijo VITE_)
export const Env = {
  appName: import.meta.env.VITE_APP_NAME || 'Presupuesto Estudiantil',
  apiUrl: import.meta.env.VITE_API_URL || '/api',
}
