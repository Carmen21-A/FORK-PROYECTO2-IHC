// Portado de lib/main.dart
import { createApp } from 'vue'
import App from './App.vue'
import { Env } from './env.js'
import { appRouter } from './router/appRouter.js'
import { AuthService } from './services/authService.js'
import { onSesionExpirada } from './services/api.js'
import './design_system/tokens.css'
import './theme/appTheme.css'

async function main() {
  document.title = Env.appName

  // Enlace del correo de recuperacion: ?token_hash=...&type=recovery
  const params = new URLSearchParams(window.location.search)
  const tokenHash = params.get('token_hash')
  const type = params.get('type')
  let initialRoute = null

  if (tokenHash !== null && type === 'recovery') {
    try {
      await AuthService.verifyRecovery(tokenHash)
      initialRoute = '/change-password'
    } catch (e) {
      if (import.meta.env.DEV) {
        console.log('Error verificando OTP:', e)
      }
    }
    // Se limpia la URL para que el token no quede en el historial del navegador
    window.history.replaceState(null, '', window.location.pathname)
  }

  onSesionExpirada(() => appRouter.push('/login'))

  if (initialRoute) {
    await appRouter.replace(initialRoute)
  }

  createApp(App).use(appRouter).mount('#app')
}

main()
