<script setup>
// Portado de lib/widgets/app_drawer.dart
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { AuthService } from '../services/authService.js'
import AppDialog from './AppDialog.vue'
import AppIcon from './AppIcon.vue'

const emit = defineEmits(['cerrar'])
const router = useRouter()
const mostrarAyuda = ref(false)

function ir(ruta) {
  emit('cerrar') // cierra el drawer
  router.push(ruta)
}

async function cerrarSesion() {
  emit('cerrar')
  await AuthService.signOut()
  router.push('/')
}
</script>

<template>
  <Teleport to="body">
    <div class="drawer-scrim" @click="emit('cerrar')" />
    <nav class="drawer" aria-label="Menú">
      <div class="drawer-header">
        <span class="bold-body-large">Menú</span>
      </div>
      <button class="drawer-item" @click="ir('/movements')">
        <AppIcon name="list_alt" />
        Movimientos
      </button>
      <button class="drawer-item" @click="ir('/metas')">
        <AppIcon name="savings" />
        Metas de Ahorro
      </button>
      <button class="drawer-item" @click="ir('/presupuestos-categoria')">
        <AppIcon name="pie_chart" filled />
        Presupuesto por Categoría
      </button>
      <button class="drawer-item" @click="ir('/history')">
        <AppIcon name="history" />
        Historial
      </button>
      <button class="drawer-item" @click="ir('/analitica')">
        <AppIcon name="monitoring" />
        Analítica
      </button>
      <button class="drawer-item" @click="ir('/change-password')">Cambiar contraseña</button>
      <button class="drawer-item" @click="mostrarAyuda = true">Ayuda</button>
      <hr class="divider" />
      <button class="drawer-item" @click="cerrarSesion">Cerrar sesión</button>
    </nav>

    <AppDialog
      v-if="mostrarAyuda"
      titulo="Acerca de la aplicación"
      @cerrar="mostrarAyuda = false"
    >
      <p>
        El Presupuesto Estudiantil te ayuda a registrar tus gastos e ingresos y controlar que no
        superes tu limite mensual.
      </p>
      <template #acciones>
        <button class="btn btn-outlined" @click="mostrarAyuda = false">Cerrar</button>
      </template>
    </AppDialog>
  </Teleport>
</template>
