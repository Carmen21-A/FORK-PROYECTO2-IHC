<script setup>
// Logo de Presupuesto Estudiantil: billetera «C.A.» con birrete, al lado del nombre de la app
import logo from '../assets/inicio/logo.png'
</script>

<template>
  <RouterLink to="/" class="marca">
    <img class="marca-icono" :src="logo" alt="" width="160" height="144" />
    <span class="marca-texto">
      Presupuesto<br />Estudiantil
    </span>
  </RouterLink>
</template>

<style scoped>
.marca {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 4px 6px 4px 0;
  border-radius: 10px;
  color: #1b2440;
  text-decoration: none;
}

.marca-icono {
  width: 62px;
  height: auto;
  flex-shrink: 0;
}

.marca-texto {
  font-size: 19px;
  font-weight: 700;
  line-height: 1.15;
}

@media (max-width: 560px) {
  .marca-icono {
    width: 48px;
  }

  .marca-texto {
    font-size: 15px;
  }
}

@media (max-width: 400px) {
  .marca-texto {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }
}
</style>
