// Analítica de interacción (Clase 21): registrar intentos de lograr algo, no clics.
// Flujo principal: Nuevo Movimiento -> movimiento_iniciado ... guardado en BD -> movimiento_guardado
import { api } from './api.js'

export const MOVIMIENTO_INICIADO = 'movimiento_iniciado' // evento de inicio: se abre el formulario de nuevo movimiento
export const MOVIMIENTO_GUARDADO = 'movimiento_guardado' // evento de éxito: el movimiento ya se guardó en la BD

// Registros enviados en esta sesión del navegador (las pruebas los revisan)
export const eventos = []

// Por defecto el registro viaja a la tabla eventos del backend; las pruebas lo reemplazan
let enviar = (registro) => api('/eventos', { method: 'POST', body: registro })

export function configurarEnvio(fn) {
  enviar = fn
}

function guardarEvento(registro) {
  eventos.push(registro)
  // La analítica nunca debe romper la app: si el envío falla, se ignora
  Promise.resolve()
    .then(() => enviar(registro))
    .catch(() => {})
}

export function track(evento, props = {}) {
  const registro = {
    evento,
    props,
    fecha: new Date().toISOString(),
  }
  guardarEvento(registro)
  console.log('[evento]', registro)
  return registro
}

// Al tocar «Nuevo Movimiento»: la persona empieza el flujo
export function iniciarMovimientoConTrack() {
  return track(MOVIMIENTO_INICIADO, {})
}

// Al tocar «Guardar»: solo se registra si el backend confirmó que se guardó.
// Solo viajan tipo y categoría (lista fija); nunca monto, descripción ni datos de la persona.
export async function guardarMovimientoConTrack(datos, guardar) {
  const guardado = await guardar(datos)
  // solo llega aquí si se guardó
  track(MOVIMIENTO_GUARDADO, {
    tipo: datos.tipo,
    categoria: datos.categoria,
  })
  return guardado
}

// Panel /analitica: SELECT evento, COUNT(*) FROM eventos GROUP BY evento (lo calcula el backend)
export const AnaliticaService = {
  async getPanel() {
    return api('/analitica')
  },
}
