<script setup>
// Portado de lib/screens/movements_screen.dart
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { MovementsService } from '../services/movementsService.js'
import { LimitesService } from '../services/limitesService.js'
import {
  EVENTOS,
  guardarMovimientoConTrack,
  iniciarMovimientoConTrack,
  motivoMontoMovimiento,
  motivoRechazoServidor,
  track,
  trackBusqueda,
} from '../services/analitica.js'
import { siguienteEstado, puedeEditarMonto } from '../utils/estadoMovimiento.js'
import {
  calcularGastoTotalMes,
  esLimiteMenorAGasto,
  superaLimiteMensual,
  validarMontoLimite,
} from '../utils/limiteMensual.js'
import { calcularTotalGastos, calcularTotalIngresos } from '../utils/movimientosFiltros.js'
import { MESES, claveMes, dartNum, fechaISO, parseDouble, parseFecha } from '../utils/formato.js'
import { OPCIONES_RECURRENCIA, TEXTO_RECURRENCIA, siguienteFecha } from '../utils/recurrencia.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import AppDialog from '../widgets/AppDialog.vue'
import AppIcon from '../widgets/AppIcon.vue'
import BottomSheet from '../widgets/BottomSheet.vue'

const router = useRouter()
const CATEGORIAS = ['Transporte', 'Comida', 'Estudios', 'Ocio', 'Otros']

// ---------- Formulario ----------
const montoTexto = ref('')
const descripcion = ref('')
const busqueda = ref('')
const tipo = ref('gasto')
const categoria = ref('Transporte')
const recurrencia = ref('') // Tarea 6: '' = no se repite
const fecha = ref(new Date())
const montoError = ref(null)
const inputFecha = ref(null)

const movimientos = ref([])
const movimientosFiltrados = ref([])
const editingId = ref(null)
const editingState = ref(null)
const limiteMensual = ref(null)
const guardando = ref(false)
const limiteMesForm = ref(null)

// ---------- Filtros ----------
const filtroTipo = ref('todos')
const filtroCategoria = ref('todos')
const filtroPeriodo = ref('todos')
const filtroEstado = ref('todos')
const mostrarFiltrosPersonalizados = ref(false)
const rangoDesde = ref(null)
const rangoHasta = ref(null)

// ---------- Pestañas de Intención (Arquitectura de Información - Clase 20) ----------
const pestanaActiva = ref('todos')

const gastosPendientes = computed(() =>
  movimientos.value.filter((m) => m.tipo === 'gasto' && m.estado === 'pendiente'),
)
const contadorPendientes = computed(() => gastosPendientes.value.length)
const totalPorPagar = computed(() =>
  gastosPendientes.value.reduce((acc, m) => acc + Number(m.monto), 0),
)

const movimientosAMostrar = computed(() => {
  if (pestanaActiva.value === 'por_pagar') {
    return gastosPendientes.value
  }
  return movimientosFiltrados.value
})

function cambiarPestana(p) {
  if (p === 'presupuestos') {
    router.push('/presupuestos-categoria')
    return
  }
  if (p === 'metas') {
    router.push('/metas')
    return
  }
  pestanaActiva.value = p
}

// ---------- Dialogos ----------
const formularioAbierto = ref(false)
const dialogoAyuda = ref(false)
const dialogoLimite = ref(null)
const dialogoRango = ref(null)
const eliminarId = ref(null)
const cancelarMovimiento = ref(null)
const menuAbierto = ref(null)

const mesActual = () => claveMes(new Date())
const mesForm = () => claveMes(fecha.value)

onMounted(() => {
  load()
  cargarLimiteForm()
  document.addEventListener('click', cerrarMenu)
})
onBeforeUnmount(() => document.removeEventListener('click', cerrarMenu))

function cerrarMenu() {
  menuAbierto.value = null
}

// Carga los movimientos (todos y filtrados) desde la API, y el limite
async function load() {
  try {
    const [data, filtrados, limite] = await Promise.all([
      MovementsService.getAll(),
      MovementsService.buscarConFiltros({
        texto: busqueda.value,
        tipo: filtroTipo.value === 'todos' ? null : filtroTipo.value,
        categoria: filtroCategoria.value === 'todos' ? null : filtroCategoria.value,
        estado: filtroEstado.value === 'todos' ? null : filtroEstado.value,
        desde: periodoDesde(),
        hasta: periodoHasta(),
      }),
      LimitesService.getLimit(mesActual()),
    ])
    movimientos.value = data
    movimientosFiltrados.value = filtrados
    limiteMensual.value = limite
  } catch (e) {
    showSnackBar(e.message, 'var(--error-default)')
  }
}

// Carga el limite del mes de la fecha del formulario (para la validacion en vivo)
async function cargarLimiteForm() {
  try {
    limiteMesForm.value = await LimitesService.getLimit(mesForm())
  } catch {
    limiteMesForm.value = null
  }
}

// Gasto del mes del formulario sin contar dos veces el movimiento que se edita
function gastoActualForm() {
  let gastoActual = calcularGastoTotalMes(movimientos.value, mesForm())
  if (editingId.value !== null) {
    const movViejo = movimientos.value.find((m) => m.id === editingId.value)
    if (movViejo && movViejo.tipo === 'gasto' && movViejo.estado !== 'cancelado') {
      gastoActual -= Number(movViejo.monto)
    }
  }
  return gastoActual
}

// Aviso en vivo cuando el monto supera el limite disponible del mes
const avisoMontoExcedido = computed(() => {
  if (tipo.value !== 'gasto') return null
  const limite = limiteMesForm.value
  if (limite === null) return null

  const monto = parseDouble(montoTexto.value)
  if (monto === null || monto <= 0) return null

  const disponible = limite - gastoActualForm()
  if (monto > disponible) {
    return `Supera tu límite mensual. Disponible: ${dartNum(disponible)} Bs de ${dartNum(limite)} Bs.`
  }
  return null
})

// Muestra el limite que esta disponible en el formulario de gasto
const indicadorLimiteForm = computed(() => {
  if (tipo.value !== 'gasto') return null
  const limite = limiteMesForm.value ?? limiteMensual.value
  if (limite === null) return null

  const disponible = limite - gastoActualForm()
  const disponibleTexto = disponible >= 0 ? `${dartNum(disponible)} Bs` : '0 Bs'
  return `Límite disponible: ${disponibleTexto} de ${dartNum(limite)} Bs`
})

// Fecha inicial del periodo seleccionado
function periodoDesde() {
  const hoy = new Date()
  if (filtroPeriodo.value === 'este mes') return new Date(hoy.getFullYear(), hoy.getMonth(), 1)
  if (filtroPeriodo.value === 'mes pasado') return new Date(hoy.getFullYear(), hoy.getMonth() - 1, 1)
  if (filtroPeriodo.value === 'rango') return rangoDesde.value
  return null
}

// Fecha final del periodo seleccionado
function periodoHasta() {
  const hoy = new Date()
  if (filtroPeriodo.value === 'este mes') return new Date(hoy.getFullYear(), hoy.getMonth() + 1, 0)
  if (filtroPeriodo.value === 'mes pasado') return new Date(hoy.getFullYear(), hoy.getMonth(), 0)
  if (filtroPeriodo.value === 'rango') return rangoHasta.value
  return null
}

// Tarea 9 Parte A: busca o filtra y registra si hubo resultados (sin guardar el texto buscado)
async function buscar() {
  await load()
  const conTexto = busqueda.value.trim() !== ''
  const conFiltros =
    filtroTipo.value !== 'todos' ||
    filtroCategoria.value !== 'todos' ||
    filtroEstado.value !== 'todos' ||
    filtroPeriodo.value !== 'todos'
  if (!conTexto && !conFiltros) return
  trackBusqueda({ conTexto, conFiltros, sinResultados: movimientosFiltrados.value.length === 0 })
}

function cambiarPeriodo(valor) {
  if (valor !== 'rango') {
    filtroPeriodo.value = valor
    buscar()
    return
  }
  dialogoRango.value = {
    desde: rangoDesde.value ? fechaISO(rangoDesde.value) : '',
    hasta: rangoHasta.value ? fechaISO(rangoHasta.value) : '',
    error: null,
  }
}

function confirmarRango() {
  const { desde, hasta } = dialogoRango.value
  if (!desde || !hasta) {
    dialogoRango.value.error = 'Elige la fecha de inicio y la de fin'
    return
  }
  if (desde > hasta) {
    dialogoRango.value.error = 'La fecha de inicio no puede ser posterior a la de fin'
    return
  }
  filtroPeriodo.value = 'rango'
  rangoDesde.value = parseFecha(desde)
  rangoHasta.value = parseFecha(hasta)
  dialogoRango.value = null
  buscar()
}

const filtros = { tipo: filtroTipo, categoria: filtroCategoria, estado: filtroEstado }

function cambiarFiltro(nombre, valor) {
  filtros[nombre].value = valor
  buscar()
}

// Chips de los filtros activos, con opcion de quitarlos
const chipsFiltros = computed(() => {
  const chips = []
  if (busqueda.value.trim() !== '') {
    chips.push({ texto: `Buscar: ${busqueda.value.trim()}`, quitar: () => { busqueda.value = '' } })
  }
  if (filtroTipo.value !== 'todos') {
    chips.push({ texto: `Tipo: ${filtroTipo.value}`, quitar: () => { filtroTipo.value = 'todos' } })
  }
  if (filtroCategoria.value !== 'todos') {
    chips.push({
      texto: `Categoría: ${filtroCategoria.value}`,
      quitar: () => { filtroCategoria.value = 'todos' },
    })
  }
  if (filtroPeriodo.value !== 'todos') {
    const texto =
      filtroPeriodo.value === 'rango'
        ? `${fechaCorta(rangoDesde.value)} - ${fechaCorta(rangoHasta.value)}`
        : filtroPeriodo.value
    chips.push({
      texto: `Periodo: ${texto}`,
      quitar: () => {
        filtroPeriodo.value = 'todos'
        rangoDesde.value = null
        rangoHasta.value = null
      },
    })
  }
  if (filtroEstado.value !== 'todos') {
    chips.push({ texto: `Estado: ${filtroEstado.value}`, quitar: () => { filtroEstado.value = 'todos' } })
  }
  return chips
})

function quitarChip(chip) {
  chip.quitar()
  load()
}

function limpiarSoloBusqueda() {
  busqueda.value = ''
  load()
}

function limpiarBusqueda() {
  busqueda.value = ''
  filtroTipo.value = 'todos'
  filtroCategoria.value = 'todos'
  filtroPeriodo.value = 'todos'
  filtroEstado.value = 'todos'
  rangoDesde.value = null
  rangoHasta.value = null
  load()
}

const totalesTexto = computed(
  () =>
    `Total gastos: ${dartNum(calcularTotalGastos(movimientosFiltrados.value))} Bs · ` +
    `Total ingresos: ${dartNum(calcularTotalIngresos(movimientosFiltrados.value))} Bs`,
)

// ---------- Tarjeta resumen del limite ----------
const resumenLimite = computed(() => {
  const gastoActual = calcularGastoTotalMes(movimientos.value, mesActual())
  const limite = limiteMensual.value
  const disponible = limite !== null ? limite - gastoActual : null
  return { gastoActual, limite, disponible }
})

// Esto sirve para cambiar el limite mensual
function dialogoCambiarLimite() {
  dialogoLimite.value = {
    texto: limiteMensual.value !== null ? dartNum(limiteMensual.value) : '',
    gastoActual: calcularGastoTotalMes(movimientos.value, mesActual()),
    error: null,
    guardando: false,
  }
}

async function guardarLimite() {
  const dialogo = dialogoLimite.value
  // Que no este vacio, sin letras y solo numeros
  dialogo.error = validarMontoLimite(dialogo.texto)
  // Verifica que no sea menor a lo ya gastado
  if (!dialogo.error && esLimiteMenorAGasto(parseDouble(dialogo.texto), dialogo.gastoActual)) {
    dialogo.error = `No puede ser menor a lo ya gastado "${dartNum(dialogo.gastoActual)} Bs"`
  }
  if (dialogo.error) return

  dialogo.guardando = true
  try {
    await LimitesService.saveMonthLimit({ mes: mesActual(), limite: parseDouble(dialogo.texto) })
    dialogoLimite.value = null
    load()
    cargarLimiteForm()
    showSnackBar(`Límite actualizado a ${dartNum(parseDouble(dialogo.texto))} Bs`, 'var(--success-dark)')
  } catch (e) {
    dialogo.guardando = false
    dialogo.error = e.message
  }
}

async function validarSiExcedioLimiteMensual(monto) {
  if (tipo.value !== 'gasto') return false

  const limite = await LimitesService.getLimit(mesForm())
  if (limite === null) return false

  const gastoActual = gastoActualForm()

  if (superaLimiteMensual({ gastoActualDelMes: gastoActual, nuevoGasto: monto, limite })) {
    showSnackBar(
      `No se puede registrar, porque supera tu límite mensual de ${dartNum(limite)} Bs (llevas gastando ${dartNum(gastoActual)} Bs)`,
      'var(--error-default)',
    )
    return true // Se excedio
  }

  return false // No se excedio
}

function validarMonto() {
  const texto = montoTexto.value
  if (texto === '') return 'El campo no puede estar vacío'
  const n = parseDouble(texto)
  if (n === null) return 'Formato numérico inválido'
  if (n <= 0) return 'El monto debe ser mayor a 0'
  return null
}

// Tarea 9: datos del aviso cuando el gasto haría pasar el presupuesto de su categoría
const avisoPresupuesto = ref(null)

// Cancelar no cambia nada: se cierra el aviso y el formulario sigue abierto para ajustar el monto
function cancelarAvisoPresupuesto() {
  // Tarea 9 Parte A: salida del embudo del aviso
  track(EVENTOS.AVISO_CANCELADO, { categoria: avisoPresupuesto.value.categoria })
  avisoPresupuesto.value = null
}

// Confirmar guarda: se vuelve a enviar indicando que el usuario aceptó pasarse
function confirmarAvisoPresupuesto() {
  // Tarea 9 Parte A: éxito del embudo del aviso
  track(EVENTOS.AVISO_CONFIRMADO, { categoria: avisoPresupuesto.value.categoria })
  avisoPresupuesto.value = null
  save(true)
}

// Tarea 9 Parte A: error que frena el registro (solo al crear, que es el embudo medido)
function trackRechazoMovimiento(motivo) {
  if (editingId.value === null) track(EVENTOS.MOVIMIENTO_RECHAZADO, { motivo })
}

async function save(confirmarExceso = false) {
  if (guardando.value) return
  montoError.value = validarMonto()
  if (montoError.value) {
    trackRechazoMovimiento(motivoMontoMovimiento(montoError.value))
    return
  }
  const monto = parseDouble(montoTexto.value) ?? 0

  guardando.value = true
  try {
    const excede = await validarSiExcedioLimiteMensual(monto)
    if (excede) {
      trackRechazoMovimiento('supera_limite_mensual')
      return
    }

    const datos = {
      tipo: tipo.value,
      monto,
      categoria: categoria.value,
      fecha: fecha.value,
      descripcion: descripcion.value.trim(),
      // Solo un gasto se repite
      recurrencia: tipo.value === 'gasto' && recurrencia.value ? recurrencia.value : null,
      // Tarea 9: true solo si el usuario ya confirmó en el aviso de presupuesto
      confirmar_exceso: confirmarExceso === true,
    }
    let mensaje
    if (editingId.value === null) {
      // Se esta creando uno (Clase 21: movimiento_guardado solo se registra si se guardó)
      await guardarMovimientoConTrack(datos, MovementsService.create)
      mensaje = `${tipo.value === 'gasto' ? 'Gasto' : 'Ingreso'} registrado: ${dartNum(monto)} Bs`
    } else {
      // Se esta editando un movimiento existente
      await MovementsService.update({ id: editingId.value, ...datos })
      editingId.value = null
      editingState.value = null
      mensaje = 'Movimiento actualizado'
    }

    // Se vuelve a cargar la lista y se confirma lo que paso
    await load()
    formularioAbierto.value = false
    montoTexto.value = ''
    descripcion.value = ''
    recurrencia.value = ''
    showSnackBar(mensaje, 'var(--success-dark)')
  } catch (e) {
    // Tarea 9: el gasto pasaría el presupuesto de su categoría -> mostrar cuánto y pedir confirmación
    if (e.status === 409 && e.datos?.codigo === 'supera_presupuesto_categoria') {
      avisoPresupuesto.value = e.datos
      // Tarea 9 Parte A: paso intermedio del embudo del aviso
      track(EVENTOS.AVISO_MOSTRADO, { categoria: e.datos.categoria })
      return
    }
    trackRechazoMovimiento(/límite mensual/.test(e.message) ? 'supera_limite_mensual' : 'rechazado_por_servidor')
    showSnackBar(e.message, 'var(--error-default)')
  } finally {
    guardando.value = false
  }
}

async function eliminar(id) {
  eliminarId.value = null
  try {
    await MovementsService.delete(id)
    load()
    showSnackBar('Movimiento eliminado', 'var(--success-dark)')
  } catch (e) {
    showSnackBar(e.message, 'var(--error-default)')
  }
}

function prepareEdition(m) {
  editingId.value = m.id
  montoTexto.value = String(m.monto)
  descripcion.value = m.descripcion ?? ''
  tipo.value = m.tipo
  categoria.value = m.categoria
  recurrencia.value = m.recurrencia ?? ''
  fecha.value = parseFecha(m.fecha)
  editingState.value = m.estado
  montoError.value = null
  cargarLimiteForm()
  formularioAbierto.value = true
}

function nuevoMovimiento() {
  editingId.value = null
  editingState.value = null
  montoTexto.value = ''
  descripcion.value = ''
  recurrencia.value = ''
  montoError.value = null
  fecha.value = new Date()
  cargarLimiteForm()
  formularioAbierto.value = true
  // Clase 21: la persona empieza el flujo principal
  iniciarMovimientoConTrack()
}

function cancelarEdicion() {
  editingId.value = null
  editingState.value = null
  montoTexto.value = ''
  descripcion.value = ''
  formularioAbierto.value = false
}

function fechaTexto(iso) {
  const d = parseFecha(iso)
  return `${d.getDate()} de ${MESES[d.getMonth()]}`
}

function fechaCorta(f) {
  if (!f) return '?'
  return `${f.getDate()}/${f.getMonth() + 1}/${f.getFullYear()}`
}

function abrirSelectorFecha() {
  const input = inputFecha.value
  if (!input) return
  if (typeof input.showPicker === 'function') {
    try {
      input.showPicker()
      return
    } catch {
      // algunos navegadores no lo permiten: se usa el campo directamente
    }
  }
  input.focus()
}

function alCambiarFecha(evento) {
  if (!evento.target.value) return
  fecha.value = parseFecha(evento.target.value)
  cargarLimiteForm()
}

async function cambiarEstado(m, confirmado = false) {
  const siguiente = siguienteEstado(m.estado)
  if (siguiente === null) return

  // Cancelar es irreversible, se pide confirmacion antes
  if (siguiente === 'cancelado' && !confirmado) {
    cancelarMovimiento.value = m
    return
  }
  cancelarMovimiento.value = null

  // Tarea 9 Parte A: inicio del embudo «Pagar un pendiente»
  const esPago = siguiente === 'pagado'
  if (esPago) track(EVENTOS.PAGO_INICIADO, { tipo: m.tipo })

  try {
    const respuesta = await MovementsService.cambiarEstado(m.id, siguiente)
    if (esPago) track(EVENTOS.MOVIMIENTO_PAGADO, { tipo: m.tipo })
    load()
    // Tarea 6: al pagar un gasto recurrente se genera el siguiente (o se avisa por que no)
    if (respuesta?.siguiente) {
      showSnackBar(
        `Se generó el próximo gasto: ${fechaTexto(respuesta.siguiente.fecha)}`,
        'var(--success-dark)',
      )
    } else if (respuesta?.aviso) {
      showSnackBar(respuesta.aviso, 'var(--error-default)')
    }
  } catch (e) {
    // Tarea 9 Parte A: permiso denegado (p. ej. el dinero está reservado en metas)
    if (esPago) track(EVENTOS.PAGO_RECHAZADO, { motivo: motivoRechazoServidor(e) })
    showSnackBar(e.message, 'var(--error-default)')
  }
}

const estadoXColor = {
  pendiente: 'var(--estado-pendiente)',
  pagado: 'var(--estado-pagado)',
  cancelado: 'var(--estado-cancelado)',
}

function montoLista(m) {
  return `${m.tipo === 'gasto' ? '-' : '+'} ${Number(m.monto)} Bs`
}

// Tarea 6: "Se repite cada semana · próxima: 10 de noviembre" (la proxima solo mientras esta pendiente)
function textoRecurrencia(m) {
  if (!m.recurrencia) return null
  const texto = `Se repite ${TEXTO_RECURRENCIA[m.recurrencia]}`
  if (m.estado !== 'pendiente') return texto
  return `${texto} · próxima: ${fechaTexto(fechaISO(siguienteFecha(parseFecha(m.fecha), m.recurrencia)))}`
}

function subtituloLista(m) {
  const desc = m.descripcion ?? ''
  return `${m.categoria} · ${fechaTexto(m.fecha)}${desc === '' ? '' : ` · ${desc}`}`
}

function alternarMenu(id) {
  menuAbierto.value = menuAbierto.value === id ? null : id
}
</script>

<template>
  <AppScaffold titulo="Movimientos" con-drawer>
    <template #acciones>
      <button class="btn btn-outlined btn-small" @click="dialogoAyuda = true">
        <AppIcon name="help" :size="18" />
        Ayuda
      </button>
    </template>

    <main class="movimientos">
      <!-- Navegación por Intención (Arquitectura de Información - Clase 20) -->
      <nav class="tabs-arquitectura" role="tablist" aria-label="Navegación por intención">
        <button
          type="button"
          role="tab"
          class="tab-item"
          :class="{ activa: pestanaActiva === 'todos' }"
          :aria-selected="pestanaActiva === 'todos'"
          @click="cambiarPestana('todos')"
        >
          <AppIcon name="receipt_long" :size="18" />
          <span>Todos los movimientos</span>
        </button>

        <button
          type="button"
          role="tab"
          class="tab-item"
          :class="{ activa: pestanaActiva === 'por_pagar' }"
          :aria-selected="pestanaActiva === 'por_pagar'"
          @click="cambiarPestana('por_pagar')"
        >
          <AppIcon name="schedule" :size="18" />
          <span>Por pagar</span>
          <span v-if="contadorPendientes > 0" class="tab-badge">{{ contadorPendientes }}</span>
        </button>

        <button
          type="button"
          role="tab"
          class="tab-item"
          :class="{ activa: pestanaActiva === 'presupuestos' }"
          :aria-selected="pestanaActiva === 'presupuestos'"
          @click="cambiarPestana('presupuestos')"
        >
          <AppIcon name="pie_chart" :size="18" />
          <span>Presupuestos</span>
        </button>

        <button
          type="button"
          role="tab"
          class="tab-item"
          :class="{ activa: pestanaActiva === 'metas' }"
          :aria-selected="pestanaActiva === 'metas'"
          @click="cambiarPestana('metas')"
        >
          <AppIcon name="savings" :size="18" />
          <span>Metas</span>
        </button>
      </nav>

      <!-- Tarjeta específica cuando la intención es "Por pagar" -->
      <section v-if="pestanaActiva === 'por_pagar'" class="card resumen-por-pagar">
        <div class="resumen-por-pagar-icono">
          <AppIcon name="schedule" :size="32" color="var(--estado-pendiente)" />
        </div>
        <div class="resumen-por-pagar-texto">
          <strong>Por pagar este mes: {{ dartNum(totalPorPagar) }} Bs</strong>
          <span>
            {{
              contadorPendientes === 0
                ? 'No tienes pagos pendientes acumulados'
                : `${contadorPendientes} ${contadorPendientes === 1 ? 'gasto pendiente' : 'gastos pendientes'} por saldar`
            }}
          </span>
        </div>
      </section>

      <!-- Tarjeta resumen del limite -->
      <section v-if="pestanaActiva === 'todos'" class="card resumen-limite">
        <div class="resumen-texto">
          <strong>
            Gastado: {{ dartNum(resumenLimite.gastoActual) }} Bs / Límite:
            {{ resumenLimite.limite !== null ? `${dartNum(resumenLimite.limite)} Bs` : 'Sin definir' }}
          </strong>
          <span
            :style="{
              color:
                resumenLimite.disponible !== null && resumenLimite.disponible <= 0
                  ? 'var(--error-default)'
                  : 'var(--text-secondary)',
            }"
          >
            {{
              resumenLimite.limite !== null
                ? `Disponible: ${dartNum(resumenLimite.disponible >= 0 ? resumenLimite.disponible : 0)} Bs`
                : 'Define un limite para controlar tus gastos'
            }}
          </span>
        </div>
        <button class="btn btn-outlined btn-small" @click="dialogoCambiarLimite">
          {{ resumenLimite.limite === null ? 'Definir' : 'Cambiar' }}
        </button>
        <button
          class="icon-btn"
          title="Presupuestos por Categoría"
          aria-label="Presupuestos por Categoría"
          @click="router.push('/presupuestos-categoria')"
        >
          <AppIcon name="pie_chart" filled color="var(--primary-base)" />
        </button>
      </section>

      <!-- Panel de busqueda y filtros -->
      <section v-if="pestanaActiva === 'todos'" class="filtros">
        <form class="row form-busqueda" role="search" @submit.prevent="buscar">
          <div class="input-busqueda-wrapper">
            <input
              v-model="busqueda"
              class="input input-busqueda"
              type="search"
              placeholder="Buscar por descripción"
              aria-label="Buscar por descripción"
              enterkeyhint="search"
            />
            <button
              v-if="busqueda.trim() !== ''"
              type="button"
              class="btn-limpiar-input"
              title="Borrar texto de búsqueda"
              aria-label="Borrar texto"
              @click="limpiarSoloBusqueda"
            >
              <AppIcon name="close" :size="18" />
            </button>
          </div>
          <button type="submit" class="btn btn-elevated">Buscar</button>
          <button
            v-if="busqueda.trim() !== ''"
            type="button"
            class="btn btn-outlined"
            title="Limpiar búsqueda"
            @click="limpiarSoloBusqueda"
          >
            Limpiar
          </button>
        </form>

        <!-- Chips de acceso rápido para Tipo (el filtro MAS usado) -->
        <div class="wrap">
          <button
            v-for="opcion in ['todos', 'gasto', 'ingreso']"
            :key="opcion"
            class="chip"
            :class="{ selected: filtroTipo === opcion }"
            :aria-pressed="filtroTipo === opcion"
            @click="cambiarFiltro('tipo', opcion)"
          >
            <AppIcon v-if="filtroTipo === opcion" name="check" :size="18" />
            {{ opcion === 'todos' ? 'Todos' : opcion === 'gasto' ? 'Gastos' : 'Ingresos' }}
          </button>
          <button
            class="btn btn-outlined btn-small"
            :aria-expanded="mostrarFiltrosPersonalizados"
            @click="mostrarFiltrosPersonalizados = !mostrarFiltrosPersonalizados"
          >
            <AppIcon :name="mostrarFiltrosPersonalizados ? 'expand_less' : 'expand_more'" :size="18" />
            Más filtros
          </button>
        </div>

        <!-- Por defecto permanecen ocultos -->
        <div v-if="mostrarFiltrosPersonalizados" class="filtros-extra">
          <label class="field">
            <span class="field-small-label">Categoría</span>
            <select
              class="select-inline"
              :value="filtroCategoria"
              @change="cambiarFiltro('categoria', $event.target.value)"
            >
              <option v-for="o in ['todos', ...CATEGORIAS]" :key="o" :value="o">{{ o }}</option>
            </select>
          </label>
          <label class="field">
            <span class="field-small-label">Período</span>
            <select
              class="select-inline"
              :value="filtroPeriodo"
              @change="cambiarPeriodo($event.target.value); $event.target.value = filtroPeriodo"
            >
              <option v-for="o in ['todos', 'este mes', 'mes pasado', 'rango']" :key="o" :value="o">
                {{ o }}
              </option>
            </select>
          </label>
          <label class="field">
            <span class="field-small-label">Estado</span>
            <select
              class="select-inline"
              :value="filtroEstado"
              @change="cambiarFiltro('estado', $event.target.value)"
            >
              <option v-for="o in ['todos', 'pendiente', 'pagado', 'cancelado']" :key="o" :value="o">
                {{ o }}
              </option>
            </select>
          </label>
        </div>

        <div v-if="chipsFiltros.length" class="wrap">
          <span v-for="chip in chipsFiltros" :key="chip.texto" class="chip">
            {{ chip.texto }}
            <button class="chip-remove" :aria-label="`Quitar ${chip.texto}`" @click="quitarChip(chip)">
              <AppIcon name="cancel" />
            </button>
          </span>
        </div>
        <p>{{ totalesTexto }}</p>
      </section>

      <!-- Lista de movimientos -->
      <ul class="lista">
        <li v-if="pestanaActiva === 'por_pagar' && movimientosAMostrar.length === 0" class="vacio">
          🎉 ¡Excelente! No tienes pagos pendientes por saldar este mes.
        </li>
        <!-- Cuenta sin movimientos: decir que hacer, no que la busqueda fallo -->
        <li v-else-if="pestanaActiva === 'todos' && movimientos.length === 0" class="vacio">
          Aún no tienes movimientos. Registra el primero con "Nuevo Movimiento".
        </li>
        <li v-else-if="pestanaActiva === 'todos' && movimientosFiltrados.length === 0" class="vacio vacio-accion">
          <p>No hay movimientos que coincidan con la búsqueda</p>
          <button
            type="button"
            class="btn btn-outlined btn-small"
            @click="limpiarBusqueda"
          >
            <AppIcon name="close" :size="16" />
            Limpiar búsqueda
          </button>
        </li>
        <li v-for="m in movimientosAMostrar" :key="m.id" class="list-tile">
          <div class="list-tile-main">
            <div
              class="monto"
              :style="{ color: m.tipo === 'gasto' ? 'var(--error-dark)' : 'var(--success-dark)' }"
            >
              {{ montoLista(m) }}
            </div>
            <div class="list-tile-subtitle meta-movimiento"><span class="badge-cat"><span class="meta-label">Categoría:</span> {{ m.categoria }}</span> · {{ fechaTexto(m.fecha) }}<template v-if="m.descripcion"> · <span class="badge-desc"><span class="meta-label">Descripción:</span> {{ m.descripcion }}</span></template></div>
            <div v-if="m.recurrencia" class="list-tile-subtitle recurrente">
              <AppIcon name="repeat" :size="16" />
              {{ textoRecurrencia(m) }}
            </div>
          </div>
          <button
            class="btn btn-outlined btn-small estado"
            :style="{ color: estadoXColor[m.estado], borderColor: estadoXColor[m.estado] }"
            :title="siguienteEstado(m.estado) ? `Cambiar a ${siguienteEstado(m.estado)}` : 'Estado final'"
            @click="cambiarEstado(m)"
          >
            {{ m.estado }}
          </button>
          <div class="menu-wrap">
            <button
              class="icon-btn"
              title="Opciones"
              aria-label="Opciones"
              :aria-expanded="menuAbierto === m.id"
              @click.stop="alternarMenu(m.id)"
            >
              <AppIcon name="more_vert" />
            </button>
            <div v-if="menuAbierto === m.id" class="menu" role="menu">
              <button class="menu-item" role="menuitem" @click="prepareEdition(m)">
                <AppIcon name="edit" :size="20" />
                Editar
              </button>
              <button
                class="menu-item"
                role="menuitem"
                style="color: var(--estado-cancelado)"
                @click="eliminarId = m.id"
              >
                <AppIcon name="delete" :size="20" />
                Eliminar
              </button>
            </div>
          </div>
        </li>
      </ul>
    </main>

    <button class="fab" @click="nuevoMovimiento">
      <AppIcon name="add" />
      Nuevo Movimiento
    </button>

    <!-- Formulario de movimiento -->
    <BottomSheet
      v-if="formularioAbierto"
      :titulo="editingId === null ? 'Nuevo gasto o ingreso' : 'Editar movimiento'"
      @cerrar="formularioAbierto = false"
    >
      <form class="formulario stack" novalidate @submit.prevent="save()">
        <!-- Si editingId NO es nulo, mostramos este aviso -->
        <div v-if="editingId !== null" class="row editando">
          <strong>Edita este movimiento</strong>
          <button type="button" class="btn btn-outlined btn-small" @click="cancelarEdicion">
            Cancelar
          </button>
        </div>

        <div class="form-opciones">
          <select v-model="tipo" class="select-inline" aria-label="Tipo">
            <option value="gasto">Gasto</option>
            <option value="ingreso">Ingreso</option>
          </select>
          <select v-model="categoria" class="select-inline" aria-label="Categoría">
            <option v-for="c in CATEGORIAS" :key="c" :value="c">{{ c }}</option>
          </select>
          <!-- Tarea 6: solo un gasto puede repetirse -->
          <select v-if="tipo === 'gasto'" v-model="recurrencia" class="select-inline" aria-label="Repetir">
            <option v-for="o in OPCIONES_RECURRENCIA" :key="o.valor" :value="o.valor">{{ o.texto }}</option>
          </select>
          <div class="row">
            <span>{{ fechaTexto(fechaISO(fecha)) }}</span>
            <span class="selector-fecha">
              <button type="button" class="btn btn-outlined btn-small" @click="abrirSelectorFecha">
                Cambiar fecha
              </button>
              <input
                ref="inputFecha"
                type="date"
                class="input-fecha-oculto"
                aria-label="Fecha del movimiento"
                min="2020-01-01"
                max="2100-12-31"
                :value="fechaISO(fecha)"
                @change="alCambiarFecha"
              />
            </span>
          </div>
        </div>

        <p v-if="indicadorLimiteForm" class="indicador-limite">{{ indicadorLimiteForm }}</p>

        <div class="field">
          <input
            v-model="montoTexto"
            class="input"
            :class="{ invalid: montoError }"
            inputmode="decimal"
            placeholder="Monto (Bs)"
            aria-label="Monto (Bs)"
            :disabled="!puedeEditarMonto(editingState ?? 'pendiente')"
          />
          <span v-if="montoError" class="field-error">{{ montoError }}</span>
          <span v-if="avisoMontoExcedido" class="aviso-monto">{{ avisoMontoExcedido }}</span>
        </div>

        <input
          v-model="descripcion"
          class="input"
          placeholder="Descripción (opcional)"
          aria-label="Descripción (opcional)"
        />

        <p v-if="!puedeEditarMonto(editingState ?? 'pendiente')" class="aviso-pagado">
          No es posible modificar el monto porque el movimiento ya fue pagado
        </p>

        <button type="submit" class="btn btn-elevated btn-block" :disabled="guardando">
          <span v-if="guardando" class="spinner" aria-label="Guardando" />
          <template v-else>Guardar</template>
        </button>
      </form>
    </BottomSheet>

    <!-- Dialogo del limite mensual -->
    <AppDialog
      v-if="dialogoLimite"
      titulo="Límite mensual de gastos"
      :dismissible="!dialogoLimite.guardando"
      @cerrar="dialogoLimite = null"
    >
      <form id="form-limite" class="stack" novalidate @submit.prevent="guardarLimite">
        <p>Gasto actual del mes: {{ dartNum(dialogoLimite.gastoActual) }} Bs</p>
        <label class="field">
          <span class="field-small-label">Nuevo límite</span>
          <input
            v-model="dialogoLimite.texto"
            class="input"
            :class="{ invalid: dialogoLimite.error }"
            inputmode="decimal"
            placeholder="Ej: 500"
          />
          <span v-if="dialogoLimite.error" class="field-error">{{ dialogoLimite.error }}</span>
        </label>
      </form>
      <template #acciones>
        <button
          class="btn btn-outlined"
          :disabled="dialogoLimite.guardando"
          @click="dialogoLimite = null"
        >
          Cancelar
        </button>
        <button
          type="submit"
          form="form-limite"
          class="btn btn-elevated"
          :disabled="dialogoLimite.guardando"
        >
          <span v-if="dialogoLimite.guardando" class="spinner" aria-label="Guardando" />
          <template v-else>Guardar</template>
        </button>
      </template>
    </AppDialog>

    <!-- Selector de rango de fechas -->
    <AppDialog v-if="dialogoRango" titulo="Elige el rango de fechas" @cerrar="dialogoRango = null">
      <div class="stack">
        <label class="field">
          <span class="field-small-label">Desde</span>
          <input v-model="dialogoRango.desde" class="input" type="date" min="2020-01-01" max="2100-12-31" />
        </label>
        <label class="field">
          <span class="field-small-label">Hasta</span>
          <input v-model="dialogoRango.hasta" class="input" type="date" min="2020-01-01" max="2100-12-31" />
        </label>
        <span v-if="dialogoRango.error" class="field-error">{{ dialogoRango.error }}</span>
      </div>
      <template #acciones>
        <button class="btn btn-outlined" @click="dialogoRango = null">Cancelar</button>
        <button class="btn btn-elevated" @click="confirmarRango">Aplicar</button>
      </template>
    </AppDialog>

    <!-- Confirmar eliminacion -->
    <AppDialog
      v-if="eliminarId"
      titulo="Confirma que quieres eliminar este movimiento"
      @cerrar="eliminarId = null"
    >
      <p>¿Estás seguro que quieres eliminar este movimiento?</p>
      <template #acciones>
        <button class="btn btn-outlined" @click="eliminarId = null">Cancelar</button>
        <button class="btn btn-elevated" @click="eliminar(eliminarId)">Eliminar</button>
      </template>
    </AppDialog>

    <!-- Tarea 9: aviso antes de superar el presupuesto de la categoría -->
    <AppDialog
      v-if="avisoPresupuesto"
      titulo="Este gasto supera tu presupuesto"
      @cerrar="cancelarAvisoPresupuesto"
    >
      <div class="stack aviso-presupuesto">
        <p>
          Si lo guardas, te pasarías
          <strong>{{ dartNum(avisoPresupuesto.exceso) }} Bs</strong>
          del presupuesto de <strong>{{ avisoPresupuesto.categoria }}</strong> este mes.
        </p>
        <dl class="aviso-detalle">
          <dt>Presupuesto de {{ avisoPresupuesto.categoria }}</dt>
          <dd>{{ dartNum(avisoPresupuesto.presupuesto) }} Bs</dd>
          <dt>Ya gastado</dt>
          <dd>{{ dartNum(avisoPresupuesto.gastado) }} Bs</dd>
          <dt>Este gasto</dt>
          <dd>{{ dartNum(avisoPresupuesto.monto) }} Bs</dd>
          <dt>Quedaría en</dt>
          <dd class="aviso-exceso">{{ dartNum(avisoPresupuesto.nuevo_total) }} Bs</dd>
        </dl>
      </div>
      <template #acciones>
        <button class="btn btn-outlined" @click="cancelarAvisoPresupuesto">Cancelar</button>
        <button class="btn btn-elevated" @click="confirmarAvisoPresupuesto">Guardar de todas formas</button>
      </template>
    </AppDialog>

    <!-- Confirmar cancelacion (irreversible) -->
    <AppDialog
      v-if="cancelarMovimiento"
      titulo="Confirmar cancelacion"
      @cerrar="cancelarMovimiento = null"
    >
      <p>¿Seguro que quieres cancelar este movimiento? Esta acción no se puede deshacer.</p>
      <template #acciones>
        <button class="btn btn-outlined" @click="cancelarMovimiento = null">Volver</button>
        <button class="btn btn-elevated" @click="cambiarEstado(cancelarMovimiento, true)">
          Cancelar movimiento
        </button>
      </template>
    </AppDialog>

    <!-- Ayuda -->
    <AppDialog v-if="dialogoAyuda" @cerrar="dialogoAyuda = false">
      <template #titulo>
        <AppIcon name="help" color="var(--estado-pendiente)" />
        Ayuda
      </template>
      <div class="ayuda">
        <strong>Límite:</strong>
        <p>
          Este es el monto máximo que tienes planeado gastar en el mes, si intentaras registrar un
          gasto que supere tu límite, la app lo bloqueará para cuidar tu presupuesto.
        </p>
        <strong>Gastos e Ingresos:</strong>
        <p>
          • Gasto: es el dinero que pagas o usas (transporte, comida, estudios, etc.), cada gasto
          que anotas se descuenta de tu límite del mes.<br />
          • Ingreso: dinero que recibes (mesada, sueldo, etc.) y no consume tu límite.
        </p>
        <strong class="ayuda-separada">Estados de los movimientos:</strong>
        <p>
          • Pendiente: movimiento registrado.<br />
          • Pagado: dinero ya desembolsado (su monto no se puede cambiar).<br />
          • Cancelado: movimiento anulado.
        </p>
      </div>
      <template #acciones>
        <button class="btn btn-outlined" @click="dialogoAyuda = false">Entendido</button>
      </template>
    </AppDialog>
  </AppScaffold>
</template>

<style scoped>
.movimientos {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 96px;
}

.resumen-limite {
  display: flex;
  align-items: center;
  gap: var(--space-s);
  margin: var(--space-s) var(--space-m);
  padding: 12px;
}

.resumen-texto {
  display: flex;
  flex: 1;
  flex-direction: column;
}

.filtros {
  display: flex;
  flex-direction: column;
  gap: var(--space-s);
  padding: var(--space-s) var(--space-m);
}

.filtros-extra {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-m);
}

.filtros-extra .field {
  width: auto;
}

.form-busqueda {
  display: flex;
  align-items: center;
  gap: var(--space-s);
}

.input-busqueda-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  align-items: center;
}

.input-busqueda-wrapper .input {
  width: 100%;
  padding-right: 36px;
}

.btn-limpiar-input {
  position: absolute;
  right: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  border-radius: 50%;
}

.btn-limpiar-input:hover {
  background: var(--surface-container-high);
  color: var(--text-primary);
}

.meta-movimiento {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  margin-top: 2px;
}

.badge-cat {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  padding: 1px 8px;
  border-radius: 4px;
  font-weight: 600;
  color: #0f172a;
}

.meta-label {
  color: #334155;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.meta-sep {
  color: #334155;
}

.badge-desc {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #0f172a;
  font-weight: 600;
}

.lista {
  margin: 0;
  padding: 0;
  list-style: none;
}

.vacio {
  padding: var(--space-l);
  text-align: center;
}

.vacio-accion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-s);
}

.vacio-accion p {
  margin: 0;
  color: var(--text-secondary);
}

.monto {
  font-size: 16px;
  font-weight: 700;
}

.estado {
  background: transparent;
}

.recurrente {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--estado-pendiente);
}

.menu-wrap {
  position: relative;
}

.formulario {
  padding: 20px;
}

/* Tarea 9: aviso antes de superar el presupuesto de la categoría */
.aviso-presupuesto p {
  margin: 0;
}

.aviso-detalle {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 6px 16px;
  margin: 0;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--warning-light);
}

.aviso-detalle dt {
  color: var(--text-secondary);
}

.aviso-detalle dd {
  margin: 0;
  font-weight: 700;
  text-align: right;
}

.aviso-exceso {
  color: var(--error-default);
}

.editando {
  justify-content: space-between;
  padding: var(--space-s);
  color: #ff9800;
}

.form-opciones {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-around;
  gap: var(--space-s);
}

.selector-fecha {
  position: relative;
}

.input-fecha-oculto {
  position: absolute;
  inset: 0;
  opacity: 0;
  pointer-events: none;
}

.indicador-limite {
  margin: 6px 0 4px;
  font-size: 13px;
  font-weight: 700;
  color: #000000;
}

.aviso-monto {
  font-size: 12px;
  color: var(--error-default);
}

.aviso-pagado {
  font-size: 12px;
  color: var(--estado-cancelado);
}

.ayuda p {
  margin-bottom: var(--space-xs);
}

.ayuda-separada {
  display: block;
  margin-top: 12px;
}

@media (max-width: 600px) {
  .resumen-limite {
    flex-wrap: wrap;
  }

  .resumen-texto {
    flex-basis: 100%;
  }

  .list-tile {
    flex-wrap: wrap;
  }
}

/* ---------- Navegación por Intención (Arquitectura de Información - Clase 20) ---------- */
.tabs-arquitectura {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 6px;
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  border-radius: 12px;
  margin-bottom: var(--space-m);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.tab-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1;
  padding: 10px 14px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary, #64748b);
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-item:hover {
  background: rgba(237, 165, 88, 0.12);
  color: var(--text-primary, #1e293b);
}

.tab-item.activa {
  background: var(--primary-base, #eda558);
  color: #1a0e04;
  font-weight: 700;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: var(--estado-pendiente, #1565c0);
  color: #ffffff;
  font-size: 11px;
  font-weight: 700;
}

.tab-item.activa .tab-badge {
  background: #1a0e04;
  color: #ffffff;
}

/* Tarjeta resumen específica de la intención "Por pagar" */
.resumen-por-pagar {
  display: flex;
  align-items: center;
  gap: var(--space-m);
  padding: var(--space-m);
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  margin-bottom: var(--space-m);
}

.resumen-por-pagar-icono {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: #dbeafe;
  flex-shrink: 0;
}

.resumen-por-pagar-texto {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.resumen-por-pagar-texto strong {
  font-size: 16px;
  color: #1e3a8a;
}

.resumen-por-pagar-texto span {
  font-size: 13px;
  color: #3b82f6;
  font-weight: 500;
}
</style>
