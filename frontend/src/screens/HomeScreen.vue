<script setup>
// Portado de lib/screens/home_screen.dart
import { useRouter } from 'vue-router'
import { Env } from '../env.js'
import logo from '../assets/icons/v1/icon_no_background.png'

const router = useRouter()
</script>

<template>
  <main class="page centered home">
    <div class="home-intro">
      <h1 class="bold-body-large">¡Bienvenido a tu {{ Env.appName }}!</h1>
      <img :src="logo" width="150" alt="" />
      <p class="regular-micro text-secondary">
        Una aplicación que te ayuda a llevar tus cuentas estudiantiles
      </p>
    </div>
    <div class="home-acciones">
      <!-- login -->
      <button class="btn btn-elevated btn-block" @click="router.push('/login')">
        Iniciar Sesión
      </button>
      <!-- registro -->
      <button class="btn btn-outlined btn-block" @click="router.push('/register')">
        Crear una cuenta
      </button>
    </div>
  </main>
</template>

<style scoped>
.home {
  min-height: 100vh;
}

.home-intro,
.home-acciones {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-xs);
  text-align: center;
}

.home-acciones {
  width: 100%;
  margin-top: var(--space-xs);
}
</style>
