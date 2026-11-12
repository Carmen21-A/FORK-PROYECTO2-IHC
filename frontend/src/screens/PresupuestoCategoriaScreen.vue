<script setup>
// Portado de lib/screens/presupuesto_categoria_screen.dart
import { computed, onMounted, ref } from 'vue'
import { MovementsService } from '../services/movementsService.js'
import { PresupuestosService } from '../services/presupuestosService.js'
import {
  EstadoPresupuesto,
  calcularGastoCategoria,
  validarMontoPresupuesto,
} from '../utils/presupuestoCategoria.js'
import { EVENTOS, motivoPresupuesto, track } from '../services/analitica.js'
import { fixed, parseDouble } from '../utils/formato.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import AppDialog from '../widgets/AppDialog.vue'
import AppIcon from '../widgets/AppIcon.vue'

const hoy = new Date()
const mesSeleccionado = ref(new Date(hoy.getFullYear(), hoy.getMonth(), 1))
const cargando = ref(true)
const error = ref(null)

const movimientos = ref([])
const resumen = ref(null)
const categoriaDetalleExpandida = ref(null)
const dialogo = ref(null)
const eliminarCategoria = ref(null)

const mesClave = computed(
  () =>
    `${mesSeleccionado.value.getFullYear()}-${String(mesSeleccionado.value.getMonth() + 1).padStart(2, '0')}`,
)

const iconosCategoria = {
  Transporte: 'directions_bus',
  Comida: 'restaurant',
  Estudios: 'school',
  Ocio: 'sports_esports',
  Otros: 'category',
}

const coloresCategoria = {
  Transporte: '#0284C7',
  Comida: '#EA580C',
  Estudios: '#7C3AED',
  Ocio: '#DB2777',
  Otros: '#475569',
}

const NOMBRES_MES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

const tituloMes = computed(
  () => `${NOMBRES_MES[mesSeleccionado.value.getMonth()]} ${mesSeleccionado.value.getFullYear()}`,
)

onMounted(cargarDatos)

async function cargarDatos() {
  cargando.value = true
  error.value = null

  try {
    const lista = await MovementsService.getAll()
    const nuevoResumen = await PresupuestosService.getResumenMensual({
      mes: mesClave.value,
      movimientos: lista,
    })
    movimientos.value = lista
    resumen.value = nuevoResumen
  } catch (e) {
    error.value = `Error al cargar presupuestos: ${e.message}`
  } finally {
    cargando.value = false
  }
}

function cambiarMes(offset) {
  const actual = mesSeleccionado.value
  mesSeleccionado.value = new Date(actual.getFullYear(), actual.getMonth() + offset, 1)
  categoriaDetalleExpandida.value = null
  cargarDatos()
}

function abrirDialogoPresupuesto(categoria, valorActual) {
  dialogo.value = {
    categoria,
    texto: valorActual > 0 ? fixed(valorActual) : '',
    error: null,
    guardando: false,
  }
  // Tarea 9 Parte A: inicio del embudo «Presupuesto por categoría»
  track(EVENTOS.PRESUPUESTO_INICIADO, { categoria })
}

function sumarAlMonto(monto) {
  const actual = parseDouble(dialogo.value.texto) ?? 0.0
  dialogo.value.texto = fixed(actual + monto)
}

async function guardarPresupuesto() {
  const d = dialogo.value
  d.error = validarMontoPresupuesto(d.texto)
  if (d.error) {
    // Tarea 9 Parte A: validación fallida con motivo de una lista fija
    track(EVENTOS.PRESUPUESTO_RECHAZADO, { motivo: motivoPresupuesto(d.error) })
    return
  }

  const nuevoMonto = parseDouble(d.texto.trim())
  d.guardando = true

  try {
    await PresupuestosService.savePresupuestoCategoria({
      mes: mesClave.value,
      categoria: d.categoria,
      monto: nuevoMonto,
    })
    // Tarea 9 Parte A: éxito (como el ejemplo de clase: ¿se guarda cuando ya superó su límite?)
    const gastado = calcularGastoCategoria({
      movimientos: movimientos.value,
      mes: mesClave.value,
      categoria: d.categoria,
    })
    track(EVENTOS.PRESUPUESTO_GUARDADO, { categoria: d.categoria, supera_limite: gastado > nuevoMonto })
    dialogo.value = null
    cargarDatos()
    showSnackBar(
      `Presupuesto para ${d.categoria} actualizado a Bs. ${fixed(nuevoMonto)}`,
      'var(--success-dark)',
    )
  } catch (e) {
    track(EVENTOS.PRESUPUESTO_RECHAZADO, { motivo: 'rechazado_por_servidor' })
    d.guardando = false
    showSnackBar(`Error al guardar: ${e.message}`, 'var(--error-default)')
  }
}

async function eliminarPresupuesto() {
  const categoria = eliminarCategoria.value
  eliminarCategoria.value = null
  try {
    await PresupuestosService.deletePresupuestoCategoria({ mes: mesClave.value, categoria })
    cargarDatos()
    showSnackBar(`Presupuesto de ${categoria} eliminado`, 'var(--gray-600)')
  } catch (e) {
    showSnackBar(e.message, 'var(--error-default)')
  }
}

function movimientosDeCategoria(categoria) {
  return movimientos.value.filter((m) => {
    const fechaStr = String(m.fecha ?? '')
    const tipo = String(m.tipo ?? '')
    const estado = String(m.estado ?? '')
    const cat = String(m.categoria ?? '')

    return (
      fechaStr.startsWith(mesClave.value) &&
      tipo === 'gasto' &&
      estado !== 'cancelado' &&
      cat === categoria
    )
  })
}

// ---------- Tarjeta resumen ----------
const porcentajeVisual = computed(() =>
  Math.min(Math.max(resumen.value.porcentajeTotal * 100, 0), 999),
)
const estaExcedidoTotal = computed(() => resumen.value.totalRestante < 0)
const colorBarraTotal = computed(() =>
  estaExcedidoTotal.value
    ? 'var(--error-default)'
    : resumen.value.porcentajeTotal >= 0.8
      ? 'var(--warning-default)'
      : '#ffffff',
)

// Tonos oscuros: el texto de estado debe tener contraste 4.5:1 (axe)
function estadoVisual(item) {
  switch (item.estado) {
    case EstadoPresupuesto.excedido:
      return {
        color: 'var(--error-dark)',
        texto: `Excedido por Bs. ${fixed(Math.abs(item.restante))}`,
        icono: 'cancel',
      }
    case EstadoPresupuesto.alerta:
      return {
        color: 'var(--warning-dark)',
        texto: `Alerta: ${(item.porcentaje * 100).toFixed(0)}% consumido`,
        icono: 'warning',
      }
    case EstadoPresupuesto.optimo:
      return {
        color: 'var(--success-dark)',
        texto: `En orden: ${(item.porcentaje * 100).toFixed(0)}% consumido`,
        icono: 'check_circle',
      }
    default:
      return { color: 'var(--gray-base)', texto: 'Sin presupuesto fijado', icono: 'info' }
  }
}

function porcentajeBarra(valor) {
  return `${Math.min(Math.max(valor, 0), 1) * 100}%`
}
</script>

<template>
  <AppScaffold titulo="Presupuesto por Categoría" con-drawer app-bar-primaria>
    <template #acciones>
      <button class="icon-btn" title="Actualizar" aria-label="Actualizar" @click="cargarDatos">
        <AppIcon name="refresh" />
      </button>
    </template>

    <div v-if="cargando" class="centro">
      <span class="spinner large" aria-label="Cargando" />
    </div>

    <div v-else-if="error" class="centro">
      <AppIcon name="error" :size="48" color="var(--error-default)" />
      <p class="medium-body-medium">{{ error }}</p>
      <button class="btn btn-elevated" @click="cargarDatos">Reintentar</button>
    </div>

    <main v-else class="page stack">
      <!-- Navegacion de mes -->
      <section class="card navegacion-mes">
        <button class="icon-btn" title="Mes anterior" aria-label="Mes anterior" @click="cambiarMes(-1)">
          <AppIcon name="chevron_left" />
        </button>
        <div class="row">
          <AppIcon name="calendar_month" :size="20" color="var(--primary-base)" />
          <h2 class="bold-body-large text-primary">{{ tituloMes }}</h2>
        </div>
        <button class="icon-btn" title="Mes siguiente" aria-label="Mes siguiente" @click="cambiarMes(1)">
          <AppIcon name="chevron_right" />
        </button>
      </section>

      <template v-if="resumen">
        <!-- Tarjeta resumen -->
        <section class="tarjeta-resumen">
          <div class="row resumen-cabecera">
            <h2 class="bold-body-medium">Resumen Mensual por Categoría</h2>
            <span class="pastilla bold-micro">{{ porcentajeVisual.toFixed(1) }}% consumido</span>
          </div>
          <div class="metricas">
            <div class="metrica">
              <AppIcon name="account_balance_wallet" :size="20" />
              <span class="regular-micro">Presupuestado</span>
              <strong class="bold-body-small">Bs. {{ fixed(resumen.totalPresupuestado) }}</strong>
            </div>
            <div class="separador" />
            <div class="metrica">
              <AppIcon name="shopping_cart" :size="20" />
              <span class="regular-micro">Consumido</span>
              <strong class="bold-body-small">Bs. {{ fixed(resumen.totalConsumido) }}</strong>
            </div>
            <div class="separador" />
            <div class="metrica">
              <AppIcon :name="estaExcedidoTotal ? 'warning' : 'savings'" :size="20" />
              <span class="regular-micro">{{ estaExcedidoTotal ? 'Exceso' : 'Restante' }}</span>
              <strong class="bold-body-small">Bs. {{ fixed(Math.abs(resumen.totalRestante)) }}</strong>
            </div>
          </div>
          <div class="progress progreso-total">
            <div
              class="progress-bar"
              :style="{
                width: resumen.totalPresupuestado > 0 ? porcentajeBarra(resumen.porcentajeTotal) : '0%',
                background: colorBarraTotal,
              }"
            />
          </div>
        </section>

        <!-- Banner de alertas -->
        <section
          v-if="resumen.categoriasExcedidas.length || resumen.categoriasAlerta.length"
          class="banner"
          :class="resumen.categoriasExcedidas.length ? 'banner-error' : 'banner-alerta'"
          role="alert"
        >
          <AppIcon
            :name="resumen.categoriasExcedidas.length ? 'error' : 'warning'"
            :color="resumen.categoriasExcedidas.length ? 'var(--error-dark)' : 'var(--warning-dark)'"
          />
          <div>
            <p v-if="resumen.categoriasExcedidas.length" class="bold-caption" style="color: var(--error-dark)">
              ¡Límite superado en: {{ resumen.categoriasExcedidas.join(', ') }}!
            </p>
            <p v-if="resumen.categoriasAlerta.length" class="regular-caption" style="color: var(--warning-dark)">
              Cerca del límite (>= 80%): {{ resumen.categoriasAlerta.join(', ') }}
            </p>
          </div>
        </section>

        <!-- Lista de categorias -->
        <section>
          <h2 class="bold-heading-small text-primary">Categorías de Gastos</h2>
          <p class="regular-caption text-secondary">
            Monitorea el consumo real frente al límite fijado para cada categoría
          </p>
        </section>

        <article
          v-for="item in resumen.items"
          :key="item.categoria"
          class="card tarjeta-categoria"
          :class="{ excedida: item.estaExcedido }"
        >
          <div class="row">
            <span
              class="avatar"
              :style="{ background: `color-mix(in srgb, ${coloresCategoria[item.categoria]} 12%, transparent)` }"
            >
              <AppIcon :name="iconosCategoria[item.categoria]" :size="22" :color="coloresCategoria[item.categoria]" />
            </span>
            <div class="list-tile-main">
              <h3 class="bold-body-medium text-primary">{{ item.categoria }}</h3>
              <span class="row bold-micro" :style="{ color: estadoVisual(item).color, gap: '4px' }">
                <AppIcon :name="estadoVisual(item).icono" :size="14" filled />
                {{ estadoVisual(item).texto }}
              </span>
            </div>
            <button
              class="icon-btn"
              :title="item.tienePresupuesto ? 'Editar presupuesto' : 'Definir presupuesto'"
              :aria-label="`${item.tienePresupuesto ? 'Editar' : 'Definir'} presupuesto de ${item.categoria}`"
              @click="abrirDialogoPresupuesto(item.categoria, item.presupuestado)"
            >
              <AppIcon
                :name="item.tienePresupuesto ? 'edit' : 'add_circle'"
                :filled="!item.tienePresupuesto"
                color="var(--primary-base)"
              />
            </button>
            <button
              v-if="item.tienePresupuesto"
              class="icon-btn"
              title="Eliminar presupuesto"
              :aria-label="`Eliminar presupuesto de ${item.categoria}`"
              @click="eliminarCategoria = item.categoria"
            >
              <AppIcon name="delete" :size="20" color="var(--error-default)" />
            </button>
          </div>

          <div class="progress">
            <div
              class="progress-bar"
              :style="{
                width: item.tienePresupuesto ? porcentajeBarra(item.porcentaje) : '0%',
                background: estadoVisual(item).color,
              }"
            />
          </div>

          <div class="cifras">
            <div>
              <span class="regular-micro text-secondary">Presupuesto</span>
              <strong class="bold-caption">
                {{ item.tienePresupuesto ? `Bs. ${fixed(item.presupuestado)}` : 'No definido' }}
              </strong>
            </div>
            <div class="centrado">
              <span class="regular-micro text-secondary">
                Consumido ({{ item.cantidadMovimientos }} gastos)
              </span>
              <strong class="bold-caption" :style="{ color: estadoVisual(item).color }">
                Bs. {{ fixed(item.consumido) }}
              </strong>
            </div>
            <div class="derecha">
              <span class="regular-micro text-secondary">
                {{ item.estaExcedido ? 'Exceso' : 'Disponible' }}
              </span>
              <strong
                class="bold-caption"
                :style="{ color: item.estaExcedido ? 'var(--error-dark)' : 'var(--success-dark)' }"
              >
                {{ item.tienePresupuesto ? `Bs. ${fixed(Math.abs(item.restante))}` : '—' }}
              </strong>
            </div>
          </div>

          <template v-if="item.cantidadMovimientos > 0">
            <hr class="divider" />
            <button
              class="ver-gastos medium-micro"
              :aria-expanded="categoriaDetalleExpandida === item.categoria"
              @click="
                categoriaDetalleExpandida =
                  categoriaDetalleExpandida === item.categoria ? null : item.categoria
              "
            >
              {{
                categoriaDetalleExpandida === item.categoria
                  ? 'Ocultar gastos'
                  : `Ver los ${item.cantidadMovimientos} gastos de ${item.categoria}`
              }}
              <AppIcon
                :name="categoriaDetalleExpandida === item.categoria ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
                :size="16"
              />
            </button>
            <ul v-if="categoriaDetalleExpandida === item.categoria" class="detalle">
              <li v-if="movimientosDeCategoria(item.categoria).length === 0">
                No hay movimientos registrados
              </li>
              <li v-for="m in movimientosDeCategoria(item.categoria)" :key="m.id" class="row">
                <div class="list-tile-main">
                  <div class="medium-caption">{{ m.descripcion || 'Sin descripción' }}</div>
                  <div class="regular-micro text-secondary">
                    {{ m.fecha }} • Estado: {{ m.estado ?? 'pendiente' }}
                  </div>
                </div>
                <strong class="bold-caption" style="color: var(--error-dark)">
                  -Bs. {{ fixed(m.monto) }}
                </strong>
              </li>
            </ul>
          </template>
        </article>
      </template>
    </main>

    <!-- Dialogo para definir/editar el presupuesto -->
    <AppDialog
      v-if="dialogo"
      :titulo="`Presupuesto: ${dialogo.categoria}`"
      :dismissible="!dialogo.guardando"
      @cerrar="dialogo = null"
    >
      <template #titulo>
        <AppIcon
          :name="iconosCategoria[dialogo.categoria] ?? 'pie_chart'"
          :color="coloresCategoria[dialogo.categoria] ?? 'var(--primary-base)'"
        />
        <span class="bold-body-large">Presupuesto: {{ dialogo.categoria }}</span>
      </template>
      <form id="form-presupuesto" class="stack" novalidate @submit.prevent="guardarPresupuesto">
        <p class="regular-caption text-secondary">
          Define el monto límite mensual para {{ tituloMes }}
        </p>
        <label class="field">
          <span class="field-small-label">Monto mensual (Bs.)</span>
          <span class="input-wrap">
            <span class="input-prefix">Bs.</span>
            <input
              v-model="dialogo.texto"
              class="input has-prefix"
              :class="{ invalid: dialogo.error }"
              inputmode="decimal"
              placeholder="Ej. 300.00"
            />
          </span>
          <span v-if="dialogo.error" class="field-error">{{ dialogo.error }}</span>
        </label>
        <div class="wrap">
          <button
            v-for="monto in [50, 100, 200, 500]"
            :key="monto"
            type="button"
            class="chip"
            @click="sumarAlMonto(monto)"
          >
            +{{ monto }} Bs
          </button>
        </div>
      </form>
      <template #acciones>
        <button class="btn btn-text" :disabled="dialogo.guardando" @click="dialogo = null">
          Cancelar
        </button>
        <button
          type="submit"
          form="form-presupuesto"
          class="btn btn-elevated"
          :disabled="dialogo.guardando"
        >
          <span v-if="dialogo.guardando" class="spinner" aria-label="Guardando" />
          <template v-else>Guardar</template>
        </button>
      </template>
    </AppDialog>

    <!-- Confirmar eliminacion -->
    <AppDialog
      v-if="eliminarCategoria"
      :titulo="`Eliminar presupuesto de ${eliminarCategoria}`"
      @cerrar="eliminarCategoria = null"
    >
      <p>¿Estás seguro de quitar el presupuesto de esta categoría para este mes?</p>
      <template #acciones>
        <button class="btn btn-text" @click="eliminarCategoria = null">Cancelar</button>
        <button class="btn btn-danger" @click="eliminarPresupuesto">Eliminar</button>
      </template>
    </AppDialog>
  </AppScaffold>
</template>

<style scoped>
.centro {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-m);
  padding: var(--space-l);
  text-align: center;
}

.page {
  max-width: 850px;
  padding: var(--space-m);
}

.navegacion-mes {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-s) var(--space-m);
}

.tarjeta-resumen {
  display: flex;
  flex-direction: column;
  gap: var(--space-m);
  padding: var(--space-l);
  border-radius: 16px;
  background: linear-gradient(135deg, var(--primary-base), var(--primary-300));
  box-shadow: 0 4px 10px color-mix(in srgb, var(--primary-base) 30%, transparent);
  color: var(--text-inverse);
}

.resumen-cabecera {
  flex-wrap: wrap;
  justify-content: space-between;
}

.pastilla {
  padding: 4px 10px;
  border-radius: 20px;
  background: rgb(255 255 255 / 0.2);
}

.metricas {
  display: flex;
  align-items: center;
}

.metrica {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  text-align: center;
}

.metrica .icon,
.metrica span {
  color: rgb(255 255 255 / 0.75);
}

.separador {
  width: 1px;
  height: 40px;
  background: rgb(255 255 255 / 0.3);
}

.progreso-total {
  background: rgb(255 255 255 / 0.25);
}

.banner {
  display: flex;
  align-items: flex-start;
  gap: var(--space-m);
  padding: var(--space-m);
  border-radius: 12px;
}

.banner-error {
  background: var(--error-light);
  border: 1px solid color-mix(in srgb, var(--error-default) 40%, transparent);
}

.banner-alerta {
  background: var(--warning-light);
  border: 1px solid color-mix(in srgb, var(--warning-default) 40%, transparent);
}

.tarjeta-categoria {
  display: flex;
  flex-direction: column;
  gap: var(--space-m);
  padding: var(--space-m);
  border: 1.5px solid transparent;
  border-radius: 14px;
}

.tarjeta-categoria.excedida {
  border-color: color-mix(in srgb, var(--error-default) 50%, transparent);
}

.tarjeta-categoria .divider {
  margin: 0;
}

.cifras {
  display: flex;
  justify-content: space-between;
  gap: var(--space-s);
  margin-top: calc(var(--space-s) - var(--space-m));
}

.cifras > div {
  display: flex;
  flex-direction: column;
}

.centrado {
  align-items: center;
  text-align: center;
}

.derecha {
  align-items: flex-end;
  text-align: right;
}

.ver-gastos {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border: none;
  background: transparent;
  color: var(--primary-400);
  cursor: pointer;
}

.detalle {
  margin: 0;
  padding: var(--space-s);
  list-style: none;
  border-radius: 8px;
  background: color-mix(in srgb, var(--gray-100) 30%, transparent);
}

.detalle li {
  padding: 4px 8px;
}
</style>
