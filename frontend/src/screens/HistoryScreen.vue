<script setup>
// Portado de lib/screens/history_screen.dart
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { HistorialService } from '../services/historialService.js'
import { filtrarHistorial, ordenarRecientePrimero } from '../utils/historial.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import AppIcon from '../widgets/AppIcon.vue'
import BottomSheet from '../widgets/BottomSheet.vue'

const router = useRouter()
const eventos = ref([])
const busqueda = ref('')
const cargado = ref(false)
const eventoDetalle = ref(null)

onMounted(load)

async function load() {
  try {
    const data = await HistorialService.getHistorial()
    eventos.value = ordenarRecientePrimero(data)
  } catch (e) {
    showSnackBar(e.message, 'var(--error-default)')
  } finally {
    cargado.value = true
  }
}

const eventosFiltrados = computed(() => filtrarHistorial(eventos.value, busqueda.value))

function fechaHora(iso) {
  const fecha = new Date(iso)
  if (Number.isNaN(fecha.getTime())) return ''
  const dos = (n) => String(n).padStart(2, '0')
  return `${dos(fecha.getDate())}/${dos(fecha.getMonth() + 1)}/${fecha.getFullYear()} ${dos(fecha.getHours())}:${dos(fecha.getMinutes())}`
}

const ACCIONES = {
  creado: {
    texto: 'Movimiento creado',
    icono: 'add_circle',
    fondo: 'var(--success-light)',
    color: 'var(--success-dark)',
  },
  editado: {
    texto: 'Movimiento editado',
    icono: 'edit',
    fondo: 'var(--primary-100)',
    color: 'var(--primary-300)',
  },
  eliminado: {
    texto: 'Movimiento eliminado',
    icono: 'delete',
    fondo: 'var(--error-light)',
    color: 'var(--error-default)',
  },
  cambio_estado: {
    texto: 'Estado cambiado',
    icono: 'swap_horiz',
    fondo: 'var(--warning-light)',
    color: 'var(--warning-dark)',
  },
  // Tarea 8: eventos de metas de ahorro (no son movimientos, pero quedan en la historia)
  meta_creada: {
    texto: 'Meta de ahorro creada',
    icono: 'savings',
    fondo: 'var(--success-light)',
    color: 'var(--success-dark)',
  },
  meta_eliminada: {
    texto: 'Meta de ahorro eliminada',
    icono: 'delete',
    fondo: 'var(--error-light)',
    color: 'var(--error-default)',
  },
  fondos_asignados: {
    texto: 'Fondos asignados a meta',
    icono: 'add_card',
    fondo: 'var(--primary-100)',
    color: 'var(--primary-300)',
  },
  fondos_retirados: {
    texto: 'Fondos retirados de meta',
    icono: 'account_balance_wallet',
    fondo: 'var(--warning-light)',
    color: 'var(--warning-dark)',
  },
  fondos_transferidos: {
    texto: 'Fondos transferidos entre metas',
    icono: 'sync_alt',
    fondo: 'var(--primary-100)',
    color: 'var(--primary-300)',
  },
}

function accion(nombre) {
  return (
    ACCIONES[nombre] ?? {
      texto: nombre,
      icono: 'history',
      fondo: 'var(--gray-100)',
      color: 'var(--gray-base)',
    }
  )
}
</script>

<template>
  <AppScaffold titulo="Historial" con-drawer>
    <template #acciones>
      <button class="icon-btn" title="Actualizar" aria-label="Actualizar" @click="load">
        <AppIcon name="refresh" />
      </button>
    </template>

    <!-- Estado vacio -->
    <div v-if="cargado && eventos.length === 0" class="centro">
      <AppIcon name="history" :size="64" color="var(--gray-300)" />
      <p class="bold-body-large">Aún no hay movimientos registrados</p>
      <p class="regular-body-small text-secondary">
        Registra tu primer movimiento y aparecerá aquí.
      </p>
      <button class="btn btn-elevated" @click="router.push('/movements')">Registrar movimiento</button>
    </div>

    <main v-else-if="eventos.length > 0" class="historial">
      <div class="busqueda">
        <div class="input-wrap">
          <AppIcon name="search" class="input-prefix-icon" />
          <input
            v-model="busqueda"
            class="input has-prefix has-suffix busqueda-input"
            type="text"
            placeholder="Escribe lo que quieres buscar"
            aria-label="Buscar en el historial"
          />
          <button
            v-if="busqueda !== ''"
            class="icon-btn input-suffix"
            aria-label="Limpiar búsqueda"
            @click="busqueda = ''"
          >
            <AppIcon name="close" />
          </button>
        </div>
      </div>

      <!-- Sin resultados -->
      <div v-if="eventosFiltrados.length === 0" class="centro">
        <AppIcon name="search_off" :size="64" color="#9e9e9e" />
        <p class="bold-body-large">Sin resultados para "{{ busqueda }}"</p>
        <p class="regular-body-small">Prueba buscando por otra palabra clave o categoría.</p>
      </div>

      <ul v-else class="lista">
        <li
          v-for="evento in eventosFiltrados"
          :key="evento.id"
          class="list-tile clickable"
          tabindex="0"
          @click="eventoDetalle = evento"
          @keydown.enter="eventoDetalle = evento"
        >
          <span class="avatar" :style="{ background: accion(evento.accion).fondo }">
            <AppIcon :name="accion(evento.accion).icono" :size="20" :color="accion(evento.accion).color" />
          </span>
          <div class="list-tile-main">
            <strong>{{ accion(evento.accion).texto }}</strong>
            <div class="list-tile-subtitle">{{ evento.detalle }}</div>
            <div class="list-tile-subtitle">{{ fechaHora(evento.created_at) }}</div>
          </div>
        </li>
      </ul>
    </main>

    <!-- Detalle del evento -->
    <BottomSheet v-if="eventoDetalle" titulo="Detalle del evento" @cerrar="eventoDetalle = null">
      <div class="detalle">
        <h2 class="bold-body-large">Detalle del evento</h2>
        <dl>
          <dt>Acción</dt>
          <dd>{{ accion(eventoDetalle.accion).texto }}</dd>
          <dt>Detalle</dt>
          <dd>{{ eventoDetalle.detalle }}</dd>
          <dt>Fecha</dt>
          <dd>{{ fechaHora(eventoDetalle.created_at) }}</dd>
        </dl>
        <button class="btn btn-outlined btn-block" @click="eventoDetalle = null">Cerrar</button>
      </div>
    </BottomSheet>
  </AppScaffold>
</template>

<style scoped>
.centro {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-xs);
  padding: var(--space-l);
  text-align: center;
}

.centro .btn {
  margin-top: 12px;
}

.historial {
  display: flex;
  flex: 1;
  flex-direction: column;
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.busqueda {
  padding: 12px var(--space-m) var(--space-s);
}

.busqueda-input {
  border-radius: 12px;
}

.lista {
  margin: 0;
  padding: 0;
  list-style: none;
}

.lista li + li {
  border-top: 1px solid var(--gray-100);
}

.detalle {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
}

dl {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: var(--space-s);
  margin: 0;
}

dt {
  font-weight: 700;
}

dd {
  margin: 0;
  overflow-wrap: anywhere;
}
</style>
