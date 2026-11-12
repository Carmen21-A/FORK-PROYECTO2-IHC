// Cliente HTTP para la API FastAPI (reemplaza al cliente de Supabase)
import { Env } from '../env.js'
import { borrarSesion, sesionActual } from './sesion.js'

export class ApiError extends Error {
  constructor(status, message, datos = null) {
    super(message)
    this.status = status
    // Tarea 9: cuando el backend responde un objeto (p. ej. el aviso de presupuesto), sus datos
    this.datos = datos
  }
}

let alExpirarSesion = () => {}

// main.js registra que hacer cuando la sesion expira (ir a /login)
export function onSesionExpirada(callback) {
  alExpirarSesion = callback
}

function mensajeDeError(detail) {
  if (typeof detail === 'string') return detail
  // Tarea 9: detalle con datos (aviso de presupuesto) trae su propio mensaje
  if (detail && typeof detail === 'object' && typeof detail.mensaje === 'string') return detail.mensaje
  // Errores de validacion de FastAPI (422)
  if (Array.isArray(detail) && detail.length > 0) {
    const campo = detail[0].loc?.at(-1)
    if (campo === 'email') return 'Ingresa un correo válido'
    return detail[0].msg ?? 'Datos inválidos'
  }
  return 'Ocurrió un error inesperado'
}

export async function api(ruta, { method = 'GET', body, params } = {}) {
  const url = new URL(`${Env.apiUrl}${ruta}`, window.location.origin)
  for (const [clave, valor] of Object.entries(params ?? {})) {
    if (valor !== null && valor !== undefined && valor !== '') url.searchParams.set(clave, valor)
  }

  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const token = sesionActual.value?.access_token
  if (token) headers.Authorization = `Bearer ${token}`

  const respuesta = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (respuesta.status === 401 && token) {
    borrarSesion()
    alExpirarSesion()
  }

  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => ({}))
    const conDatos = datos.detail && typeof datos.detail === 'object' && !Array.isArray(datos.detail)
    throw new ApiError(respuesta.status, mensajeDeError(datos.detail), conDatos ? datos.detail : null)
  }

  if (respuesta.status === 204) return null
  return respuesta.json()
}
