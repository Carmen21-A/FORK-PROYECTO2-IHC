<script setup>
// Barra superior de las páginas públicas (Inicio, Iniciar Sesión y Crear Cuenta).
// En cada página se muestra solo la acción que lleva a otra parte:
// en el login no aparece «Iniciar Sesión» y en el registro no aparece «Crear Cuenta».
import { useRouter } from 'vue-router'
import MarcaLogo from './MarcaLogo.vue'

const props = defineProps({
  pagina: { type: String, required: true }, // 'inicio' | 'login' | 'registro'
  transparente: { type: Boolean, default: false }, // sin fondo blanco, sobre una imagen de fondo
  sinMarca: { type: Boolean, default: false }, // el fondo ya trae el logo: en escritorio no se repite
  soloMarca: { type: Boolean, default: false }, // solo el logo (el registro ya tiene su enlace a «Iniciar Sesión»)
})

const router = useRouter()
const enInicio = props.pagina === 'inicio'
</script>

<template>
  <header class="pub-barra" :class="{ 'pub-barra-transparente': transparente, 'pub-barra-sin-marca': sinMarca }">
    <div class="pub-contenedor pub-barra-fila">
      <MarcaLogo class="pub-barra-marca" />
      <nav v-if="!soloMarca" class="pub-nav" aria-label="Secciones">
        <a :href="enInicio ? '#inicio' : '/'" @click="!enInicio && ($event.preventDefault(), router.push('/'))">Inicio</a>
        <a
          :href="enInicio ? '#beneficios' : '/#beneficios'"
          @click="!enInicio && ($event.preventDefault(), router.push({ path: '/', hash: '#beneficios' }))"
        >
          Beneficios
        </a>
      </nav>
      <div v-if="!soloMarca" class="pub-acciones">
        <button v-if="pagina !== 'login'" type="button" class="pub-btn pub-btn-texto" @click="router.push('/login')">
          Iniciar Sesión
        </button>
        <button v-if="pagina !== 'registro'" type="button" class="pub-btn pub-btn-primario" @click="router.push('/register')">
          Crear Cuenta
        </button>
      </div>
    </div>
  </header>
</template>
