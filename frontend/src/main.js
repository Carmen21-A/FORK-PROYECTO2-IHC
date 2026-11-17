// Portado de lib/main.dart
import { createApp } from 'vue'
import App from './App.vue'
import { Env } from './env.js'
import { appRouter } from './router/appRouter.js'
import { onSesionExpirada } from './services/api.js'
import './design_system/tokens.css'
import './theme/appTheme.css'

function main() {
  document.title = Env.appName

  // La recuperación de contraseña ya no usa enlaces (?token_hash=...): ahora es un código
  // de 4 dígitos que se escribe en /reset-password, así que aquí no hay nada que leer de la URL.
  onSesionExpirada(() => appRouter.push('/login'))

  createApp(App).use(appRouter).mount('#app')
}

main()
