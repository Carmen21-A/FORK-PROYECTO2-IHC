<script setup>
// Clase 21 + Tarea 9 (Parte A): panel propio de analítica.
// Lee la tabla eventos y muestra un embudo por flujo principal, la caída entre pasos,
// los errores por motivo y las búsquedas sin resultados.
import { onMounted, ref } from 'vue'
import { AnaliticaService, MOVIMIENTO_GUARDADO, MOVIMIENTO_INICIADO } from '../services/analitica.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import AppIcon from '../widgets/AppIcon.vue'

const panel = ref({
  iniciados: 0,
  guardados: 0,
  porcentaje_terminan: 0,
  conteos: [],
  ultimos: [],
  embudos: [],
  mayor_caida: null,
  busquedas: { realizadas: 0, sin_resultados: 0, porcentaje_sin_resultados: 0 },
})
const cargado = ref(false)

// Qué cambiaríamos si la mayor caída está en ese flujo (decisión de diseño)
const QUE_CAMBIARIA = {
  'Registrar movimiento':
    'Mostrar el límite disponible dentro del formulario y validar el monto mientras se escribe, antes de tocar «Guardar».',
  'Aviso de presupuesto (Tarea 9)':
    'Mostrar cuánto queda del presupuesto de la categoría al elegirla, para que el aviso no sorprenda al final.',
  'Pagar un pendiente':
    'Advertir en «Por pagar» cuándo un pago tocaría dinero reservado en metas, antes de que la persona lo intente.',
  'Crear meta de ahorro (Tarea 8)':
    'Simplificar el formulario de la meta: proponer una fecha límite y un monto de ejemplo, y marcar los campos obligatorios.',
  'Mover fondos en metas (Tarea 8)':
    'Mostrar el máximo que se puede mover y un botón «Usar todo», para no escribir montos imposibles.',
  'Presupuesto por categoría':
    'Usar los botones de montos rápidos y un ejemplo en el campo, para evitar presupuestos vacíos o con letras.',
}

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

// Ancho de la barra de cada paso, relativo al primer paso del embudo
function anchoBarra(embudo, paso) {
  const inicio = embudo.pasos[0].total
  if (inicio === 0) return '0%'
  return `${Math.max(Math.round((paso.total / inicio) * 100), paso.total > 0 ? 4 : 0)}%`
}

function esMayorCaida(embudo, paso) {
  const mc = panel.value.mayor_caida
  return mc && mc.caida > 0 && mc.flujo === embudo.nombre && mc.hasta === paso.evento
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
        <strong>Pregunta:</strong> en cada flujo principal, ¿cuántas personas empiezan, cuántas terminan
        y en qué paso se traba la gente?
      </p>

      <!-- Flujo principal (Clase 21) -->
      <section class="tarjetas" aria-label="Flujo principal: registrar movimiento">
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

      <!-- Tarea 9: el paso con la mayor caída y qué cambiaríamos -->
      <section v-if="panel.mayor_caida && panel.mayor_caida.caida > 0" class="mayor-caida" data-testid="mayor-caida">
        <AppIcon name="trending_down" :size="22" />
        <div>
          <strong>Mayor caída: −{{ panel.mayor_caida.caida }} % en «{{ panel.mayor_caida.flujo }}»</strong>
          <p>
            Entre <code>{{ panel.mayor_caida.desde }}</code> y <code>{{ panel.mayor_caida.hasta }}</code>.
            <br />
            <strong>Qué cambiaríamos:</strong> {{ QUE_CAMBIARIA[panel.mayor_caida.flujo] }}
          </p>
        </div>
      </section>

      <!-- Tarea 9: un embudo por flujo principal -->
      <section class="embudos">
        <h3>Embudos por flujo</h3>
        <article
          v-for="embudo in panel.embudos"
          :key="embudo.id"
          class="embudo"
          :data-testid="`embudo-${embudo.id}`"
        >
          <header class="embudo-cabecera">
            <h4>{{ embudo.nombre }}</h4>
            <span class="terminan">{{ embudo.porcentaje_terminan }} % terminan</span>
          </header>

          <div v-for="(paso, i) in embudo.pasos" :key="paso.evento" class="paso">
            <p v-if="i > 0" class="caida" :class="{ peor: esMayorCaida(embudo, paso) }">
              ↓ −{{ paso.caida }} %<span v-if="esMayorCaida(embudo, paso)">: aquí se pierde más gente</span>
            </p>
            <div class="paso-fila">
              <code class="paso-nombre">{{ paso.evento }}</code>
              <strong class="paso-total" :data-testid="`paso-${paso.evento}`">{{ paso.total }}</strong>
            </div>
            <div class="barra-fondo">
              <div class="barra" :class="{ exito: i === embudo.pasos.length - 1 }" :style="{ width: anchoBarra(embudo, paso) }" />
            </div>
          </div>

          <div class="errores">
            <span class="errores-titulo">
              <AppIcon name="error" :size="16" />
              <code>{{ embudo.evento_error }}</code>:
              <strong :data-testid="`errores-${embudo.id}`">{{ embudo.total_errores }}</strong>
            </span>
            <ul v-if="embudo.motivos.length > 0" class="motivos">
              <li v-for="m in embudo.motivos" :key="m.motivo" :data-testid="`motivo-${embudo.id}-${m.motivo}`">
                <code>{{ m.motivo }}</code> · {{ m.total }}
              </li>
            </ul>
          </div>
        </article>
      </section>

      <!-- Tarea 9: búsquedas y filtros sin resultados -->
      <section class="busquedas" aria-label="Búsquedas sin resultados">
        <h3>Buscar y filtrar</h3>
        <p>
          <strong data-testid="busquedas-realizadas">{{ panel.busquedas?.realizadas ?? 0 }}</strong>&nbsp;<code>busqueda_realizada</code>
          ·
          <strong data-testid="busquedas-sin-resultados">{{ panel.busquedas?.sin_resultados ?? 0 }}</strong>&nbsp;<code>busqueda_sin_resultados</code>
          ({{ panel.busquedas?.porcentaje_sin_resultados ?? 0 }} % sin resultados)
        </p>
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
          Se registra la acción, no a la persona: no se guardan email, nombre, descripción, monto, nombre de
          metas ni texto buscado. Solo el nombre del evento, valores de listas fijas (tipo, categoría,
          operación, motivo) y la fecha.
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

.mayor-caida {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--error-light);
  color: var(--error-default);
}

.mayor-caida p {
  margin: 4px 0 0;
  color: var(--text-primary, #0f172a);
  font-size: 14px;
}

h3 {
  margin: 0 0 8px;
  font-size: 16px;
}

.embudos {
  display: flex;
  flex-direction: column;
  gap: var(--space-m);
}

.embudo {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: var(--space-m) var(--space-l);
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  border-radius: 14px;
}

.embudo-cabecera {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.embudo-cabecera h4 {
  margin: 0;
  font-size: 15px;
}

.terminan {
  font-size: 13px;
  font-weight: 700;
  color: var(--success-dark);
}

.paso-fila {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.paso-nombre {
  font-size: 13px;
  overflow-wrap: anywhere;
}

.barra-fondo {
  height: 12px;
  border-radius: 999px;
  background: var(--gray-100, #f1f5f9);
  overflow: hidden;
}

.barra {
  height: 100%;
  border-radius: 999px;
  background: var(--primary-300, #6366f1);
}

.barra.exito {
  background: var(--success-dark);
}

.caida {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
}

.caida.peor {
  color: var(--error-default);
}

.errores {
  border-top: 1px solid var(--gray-200, #e2e8f0);
  padding-top: 8px;
  font-size: 13px;
}

.errores-titulo {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--error-default);
}

.motivos {
  margin: 6px 0 0;
  padding-left: 22px;
  color: var(--text-secondary);
}

.busquedas,
.ultimos {
  padding: var(--space-m) var(--space-l);
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  border-radius: 14px;
}

.busquedas p {
  margin: 0;
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
  padding: 10px 14px;
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
