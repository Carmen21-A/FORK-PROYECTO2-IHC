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

// ---------- Tarea 9 · Parte A: analítica en todo el producto ----------
// Un embudo por flujo principal + errores con motivo de una lista fija + búsquedas sin resultados.
export const EVENTOS = Object.freeze({
  // Flujo 1 · Registrar movimiento
  MOVIMIENTO_INICIADO,
  MOVIMIENTO_GUARDADO,
  MOVIMIENTO_RECHAZADO: 'movimiento_rechazado',
  // Flujo 2 · Aviso antes de superar el límite (Tarea 9 Parte B)
  AVISO_MOSTRADO: 'aviso_presupuesto_mostrado',
  AVISO_CONFIRMADO: 'aviso_presupuesto_confirmado',
  AVISO_CANCELADO: 'aviso_presupuesto_cancelado',
  // Flujo 3 · Pagar un pendiente
  PAGO_INICIADO: 'pago_iniciado',
  MOVIMIENTO_PAGADO: 'movimiento_pagado',
  PAGO_RECHAZADO: 'pago_rechazado',
  // Flujo 4 · Crear meta de ahorro (Tarea 8)
  META_CREACION_INICIADA: 'meta_creacion_iniciada',
  META_CREADA: 'meta_creada',
  META_RECHAZADA: 'meta_rechazada',
  // Flujo 5 · Mover fondos en metas (Tarea 8)
  FONDOS_INICIADA: 'fondos_operacion_iniciada',
  FONDOS_REALIZADA: 'fondos_operacion_realizada',
  FONDOS_RECHAZADA: 'fondos_operacion_rechazada',
  // Flujo 6 · Presupuesto por categoría
  PRESUPUESTO_INICIADO: 'presupuesto_edicion_iniciada',
  PRESUPUESTO_GUARDADO: 'presupuesto_categoria_guardado',
  PRESUPUESTO_RECHAZADO: 'presupuesto_rechazado',
  // Flujo 7 · Buscar y filtrar
  BUSQUEDA_REALIZADA: 'busqueda_realizada',
  BUSQUEDA_SIN_RESULTADOS: 'busqueda_sin_resultados',
})

// Motivos de una lista fija: se traduce el mensaje de error a un código, nunca se envía el texto
export function motivoMontoMovimiento(mensajeError) {
  if (mensajeError === 'El campo no puede estar vacío') return 'monto_vacio'
  return 'monto_invalido'
}

export function motivoPresupuesto(mensajeError) {
  if (mensajeError === 'El presupuesto no debe estar vacío') return 'vacio'
  if (mensajeError === 'No se permiten letras, ingresa un número válido') return 'letras'
  return 'menor_o_igual_a_cero'
}

export function motivoRechazoServidor(error) {
  // 409 de la regla de metas (Tarea 8) al pagar un gasto con dinero reservado
  if (error?.status === 409 && /reservados en tus metas/.test(error.message ?? '')) {
    return 'fondos_reservados_en_metas'
  }
  return 'rechazado_por_servidor'
}

// Búsqueda: solo si hubo texto y/o filtros (sí/no), nunca el texto buscado
export function trackBusqueda({ conTexto, conFiltros, sinResultados }) {
  const props = { con_texto: conTexto, con_filtros: conFiltros }
  track(EVENTOS.BUSQUEDA_REALIZADA, props)
  if (sinResultados) track(EVENTOS.BUSQUEDA_SIN_RESULTADOS, props)
}

// Panel /analitica: SELECT evento, COUNT(*) FROM eventos GROUP BY evento (lo calcula el backend)
export const AnaliticaService = {
  async getPanel() {
    return api('/analitica')
  },
}
