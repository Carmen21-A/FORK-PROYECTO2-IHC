// Guarda la sesion en el navegador para que la app recuerde al usuario al reiniciarla
import { ref } from 'vue'

const CLAVE = 'presupuesto.sesion'

function leer() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE)) ?? null
  } catch {
    return null
  }
}

// Equivale a Supabase.instance.client.auth.currentSession
export const sesionActual = ref(leer())

export function guardarSesion(sesion) {
  sesionActual.value = sesion
  try {
    localStorage.setItem(CLAVE, JSON.stringify(sesion))
  } catch {
    // Sin almacenamiento (modo privado): la sesion dura mientras la pestaña este abierta
  }
}

export function borrarSesion() {
  sesionActual.value = null
  try {
    localStorage.removeItem(CLAVE)
  } catch {
    // nada que borrar
  }
}
