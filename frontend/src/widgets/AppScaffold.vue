<script setup>
// Equivale a Scaffold + AppBar (+ Drawer) de Flutter
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppDrawer from './AppDrawer.vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  titulo: { type: String, required: true },
  conDrawer: { type: Boolean, default: false },
  conAtras: { type: Boolean, default: false },
  appBarPrimaria: { type: Boolean, default: false },
})

const router = useRouter()
const drawerAbierto = ref(false)

function atras() {
  if (window.history.state?.back) router.back()
  else router.push('/')
}
</script>

<template>
  <div class="scaffold">
    <header class="app-bar" :class="{ primary: props.appBarPrimaria }">
      <button
        v-if="conDrawer"
        class="icon-btn"
        aria-label="Abrir menú"
        @click="drawerAbierto = true"
      >
        <AppIcon name="menu" />
      </button>
      <button v-else-if="conAtras" class="icon-btn" aria-label="Volver" @click="atras">
        <AppIcon name="arrow_back" />
      </button>
      <h1 class="app-bar-title">{{ titulo }}</h1>
      <div class="app-bar-actions">
        <slot name="acciones" />
      </div>
    </header>
    <slot />
    <AppDrawer v-if="drawerAbierto" @cerrar="drawerAbierto = false" />
  </div>
</template>
