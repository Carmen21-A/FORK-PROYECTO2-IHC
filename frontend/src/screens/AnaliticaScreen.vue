<script setup>
// Clase 21: panel propio de analítica. Lee la tabla eventos y muestra cuántos empiezan y cuántos terminan.
import { onMounted, ref } from 'vue'
import { AnaliticaService, MOVIMIENTO_GUARDADO, MOVIMIENTO_INICIADO } from '../services/analitica.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import AppIcon from '../widgets/AppIcon.vue'

const panel = ref({ iniciados: 0, guardados: 0, porcentaje_terminan: 0, conteos: [], ultimos: [] })
const cargado = ref(false)

onMounted(cargar)

async function cargar() {
  try {
    panel.value = await AnaliticaService.getPanel()
  } catch (e) {
    showSnackBar(e.message, 'var(--error-default)')
  } finally {
    cargado.value = true
  }
}

// "tipo: gasto · categoria: Comida" (o "sin propiedades")
function textoProps(props) {
  const pares = Object.entries(props ?? {})
  if (pares.length === 0) return 'sin propiedades'
  return pares.map(([clave, valor]) => `${clave}: ${valor}`).join(' · ')
}

function hora(iso) {
  const f = new Date(iso)
  if (Number.isNaN(f.getTime())) return ''
  const dos = (n) => String(n).padStart(2, '0')
  return `${dos(f.getDate())}/${dos(f.getMonth() + 1)} ${dos(f.getHours())}:${dos(f.getMinutes())}`
}
</script>

<template>
  <AppScaffold titulo="Analítica" con-drawer>
    <template #acciones>
      <button class="btn btn-outlined btn-small" @click="cargar">
        <AppIcon name="refresh" :size="18" />
        Actualizar
      </button>
    </template>

    <main class="analitica-screen">
      <header class="encabezado">
        <h2 class="titulo">/analitica · Presupuesto Estudiantil</h2>
        <span class="etiqueta-dev">solo desarrollo</span>
      </header>
      <p class="pregunta">
        <strong>Pregunta:</strong> de las personas que empiezan a registrar un movimiento,
        ¿cuántas lo terminan de guardar?
      </p>

      <section class="tarjetas" aria-label="Resumen de eventos">
        <div class="tarjeta">
          <strong class="numero" data-testid="total-iniciados">{{ panel.iniciados }}</strong>
          <code>{{ MOVIMIENTO_INICIADO }}</code>
        </div>
        <div class="tarjeta">
          <strong class="numero" data-testid="total-guardados">{{ panel.guardados }}</strong>
          <code>{{ MOVIMIENTO_GUARDADO }}</code>
        </div>
        <div class="tarjeta destacada">
          <strong class="numero" data-testid="porcentaje-terminan">{{ panel.porcentaje_terminan }} %</strong>
          <span>terminan</span>
        </div>
      </section>

      <section class="ultimos">
        <h3>Últimos eventos</h3>
        <p v-if="cargado && panel.ultimos.length === 0" class="vacio">
          Todavía no hay eventos. Registra un movimiento con «Nuevo Movimiento» y vuelve aquí.
        </p>
        <ul v-else class="lista">
          <li v-for="(e, i) in panel.ultimos" :key="i" class="evento">
            <code class="nombre">{{ e.evento }}</code>
            <span class="detalle">{{ textoProps(e.props) }} · {{ hora(e.fecha) }}</span>
          </li>
        </ul>
      </section>

      <aside class="privacidad">
        <AppIcon name="shield" :size="20" />
        <p>
          Se registra la acción, no a la persona: no se guardan email, nombre, descripción ni monto.
          Solo el nombre del evento, el tipo y la categoría (de una lista fija) y la fecha.
        </p>
      </aside>
    </main>
  </AppScaffold>
</template>

<style scoped>
.analitica-screen {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-m);
  display: flex;
  flex-direction: column;
  gap: var(--space-m);
}

.encabezado {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.titulo {
  margin: 0;
  font-size: 18px;
}

.etiqueta-dev {
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--warning-light);
  color: var(--warning-dark);
}

.pregunta {
  margin: 0;
  color: var(--text-secondary);
}

.tarjetas {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-m);
}

.tarjeta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: var(--space-l);
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  border-radius: 14px;
}

.tarjeta code {
  font-size: 13px;
  color: var(--text-secondary);
  overflow-wrap: anywhere;
}

.numero {
  font-size: 32px;
  font-weight: 800;
}

.destacada {
  background: var(--success-light);
  border-color: var(--success-dark);
  color: var(--success-dark);
}

.ultimos h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.lista {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.evento {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 12px 16px;
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  border-radius: 10px;
}

.nombre {
  font-weight: 700;
}

.detalle {
  font-size: 13px;
  color: var(--text-secondary);
}

.vacio {
  color: var(--text-secondary);
}

.privacidad {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--primary-100);
  color: var(--text-primary, #0f172a);
  font-size: 13px;
}

.privacidad p {
  margin: 0;
}

@media (max-width: 600px) {
  .tarjetas {
    grid-template-columns: 1fr;
  }
}
</style>
