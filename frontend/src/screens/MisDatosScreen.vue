<script setup>
// Tarea 10 · Mis datos y salida honesta
// La persona ve lo que la app guarda de ella, lo descarga (CSV o JSON) y puede eliminar su cuenta.
// Regla de Presupuesto Estudiantil: se elimina todo (movimientos, presupuestos y metas);
// antes puede descargar sus movimientos.
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { CuentaService } from '../services/cuentaService.js'
import { EVENTOS, track, trackSoloLocal } from '../services/analitica.js'
import {
  NOMBRES_DATOS,
  cantidadCon,
  consecuenciasEliminar,
  descargarArchivo,
  movimientosACsv,
  nombreArchivo,
} from '../utils/misDatos.js'
import { dartNum, parseFecha } from '../utils/formato.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import AppDialog from '../widgets/AppDialog.vue'
import AppIcon from '../widgets/AppIcon.vue'

const router = useRouter()
const datos = ref(null)
const cargando = ref(true)
const errorCarga = ref(null)
const dialogoEliminar = ref(false)
const eliminando = ref(false)

const resumen = computed(() => datos.value?.resumen ?? {})
const consecuencias = computed(() => consecuenciasEliminar(resumen.value))
const movimientos = computed(() => datos.value?.movimientos ?? [])

onMounted(cargar)

async function cargar() {
  cargando.value = true
  errorCarga.value = null
  try {
    datos.value = await CuentaService.misDatos()
  } catch (e) {
    errorCarga.value = e.message
  } finally {
    cargando.value = false
  }
}

function fechaCorta(iso) {
  if (!iso) return ''
  return parseFecha(iso).toLocaleDateString('es-BO', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// ---------- Descargar ----------
function descargarCsv() {
  descargarArchivo(movimientosACsv(movimientos.value), nombreArchivo('movimientos', 'csv'), 'text/csv;charset=utf-8')
  track(EVENTOS.DATOS_DESCARGADOS, { formato: 'csv' })
  showSnackBar('Se descargaron tus movimientos (CSV)', 'var(--success-dark)')
}

function descargarJson() {
  descargarArchivo(
    JSON.stringify(datos.value, null, 2),
    nombreArchivo('mis-datos', 'json'),
    'application/json;charset=utf-8',
  )
  track(EVENTOS.DATOS_DESCARGADOS, { formato: 'json' })
  showSnackBar('Se descargaron todos tus datos (JSON)', 'var(--success-dark)')
}

// ---------- Eliminar la cuenta ----------
function abrirEliminar() {
  dialogoEliminar.value = true
  track(EVENTOS.CUENTA_ELIMINACION_INICIADA, {})
}

// Conservar no cambia nada y no pregunta «¿seguro?»: cierra el diálogo y listo
function conservar() {
  if (eliminando.value) return
  dialogoEliminar.value = false
  track(EVENTOS.CUENTA_ELIMINACION_FRENADA, { motivo: 'conservo_la_cuenta' })
}

async function eliminar() {
  eliminando.value = true
  try {
    await CuentaService.eliminarCuenta()
    trackSoloLocal(EVENTOS.CUENTA_ELIMINADA, {})
    dialogoEliminar.value = false
    await router.push('/')
    showSnackBar('Tu cuenta y todos tus datos se eliminaron.', 'var(--success-dark)', 8000)
  } catch (e) {
    track(EVENTOS.CUENTA_ELIMINACION_FRENADA, { motivo: 'rechazado_por_servidor' })
    showSnackBar(`No se pudo eliminar la cuenta: ${e.message} Tus datos siguen intactos; intenta de nuevo.`, 'var(--error-default)')
  } finally {
    eliminando.value = false
  }
}
</script>

<template>
  <AppScaffold titulo="Mis datos" con-drawer>
    <main class="page mis-datos">
      <p v-if="cargando" class="text-secondary">Cargando tus datos...</p>

      <section v-else-if="errorCarga" class="card bloque">
        <p>No se pudieron cargar tus datos: {{ errorCarga }}</p>
        <button class="btn btn-outlined" @click="cargar">Reintentar</button>
      </section>

      <template v-else>
        <!-- 1 · Ver -->
        <section class="card bloque" aria-labelledby="titulo-cuenta">
          <h2 id="titulo-cuenta" class="titulo-bloque">
            <AppIcon name="person" /> Tu cuenta
          </h2>
          <dl class="datos-cuenta">
            <template v-if="datos.cuenta.nombre">
              <dt>Nombre</dt>
              <dd>{{ datos.cuenta.nombre }}</dd>
            </template>
            <dt>Correo</dt>
            <dd>{{ datos.cuenta.email }}</dd>
            <dt>Cuenta creada</dt>
            <dd>{{ fechaCorta(datos.cuenta.creada_en) }}</dd>
          </dl>
        </section>

        <section class="card bloque" aria-labelledby="titulo-guardado">
          <h2 id="titulo-guardado" class="titulo-bloque">
            <AppIcon name="database" /> Lo que la app guarda de ti
          </h2>
          <ul class="resumen" data-testid="resumen-datos">
            <li v-for="(_, clave) in NOMBRES_DATOS" :key="clave">
              {{ cantidadCon(resumen[clave] ?? 0, clave) }}
            </li>
          </ul>
          <p class="nota">
            Tu contraseña no se guarda en texto ni se descarga. La analítica de la app cuenta acciones
            (por ejemplo, «se guardó un gasto»), pero no guarda tu correo, tus montos ni lo que escribes.
          </p>

          <!-- 1 · Descargar -->
          <div class="acciones">
            <button class="btn btn-outlined" @click="descargarCsv">
              <AppIcon name="download" /> Descargar movimientos (CSV)
            </button>
            <button class="btn btn-outlined" @click="descargarJson">
              <AppIcon name="download" /> Descargar todos mis datos (JSON)
            </button>
          </div>
        </section>

        <section class="card bloque" aria-labelledby="titulo-movimientos">
          <h2 id="titulo-movimientos" class="titulo-bloque">
            <AppIcon name="list_alt" /> Tus movimientos
          </h2>
          <p v-if="movimientos.length === 0" class="text-secondary">Aún no tienes movimientos.</p>
          <div v-else class="tabla-scroll">
            <table class="tabla">
              <thead>
                <tr>
                  <th scope="col">Fecha</th>
                  <th scope="col">Tipo</th>
                  <th scope="col">Categoría</th>
                  <th scope="col">Descripción</th>
                  <th scope="col" class="num">Monto</th>
                  <th scope="col">Estado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(m, i) in movimientos" :key="i">
                  <td>{{ fechaCorta(m.fecha) }}</td>
                  <td>{{ m.tipo }}</td>
                  <td>{{ m.categoria }}</td>
                  <td>{{ m.descripcion }}</td>
                  <td class="num">{{ dartNum(m.monto) }} Bs</td>
                  <td>{{ m.estado }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <details v-if="datos.presupuestos_categoria.length || datos.limites_mensuales.length || datos.metas_ahorro.length">
            <summary>Ver límites, presupuestos y metas</summary>
            <ul class="lista-simple">
              <li v-for="l in datos.limites_mensuales" :key="`l-${l.mes}`">
                Límite mensual {{ l.mes }}: {{ dartNum(l.limite) }} Bs
              </li>
              <li v-for="p in datos.presupuestos_categoria" :key="`p-${p.mes}-${p.categoria}`">
                Presupuesto {{ p.categoria }} ({{ p.mes }}): {{ dartNum(p.monto) }} Bs
              </li>
              <li v-for="(meta, i) in datos.metas_ahorro" :key="`m-${i}`">
                Meta «{{ meta.nombre }}»: {{ dartNum(meta.monto_ahorrado) }} de {{ dartNum(meta.monto_objetivo) }} Bs
              </li>
            </ul>
          </details>
        </section>

        <!-- 2 · Eliminar la cuenta: tan a mano como crearla -->
        <section class="card bloque" aria-labelledby="titulo-eliminar">
          <h2 id="titulo-eliminar" class="titulo-bloque">
            <AppIcon name="person_remove" /> Eliminar mi cuenta
          </h2>
          <p>
            Se borra tu cuenta y todo lo que guardaste: movimientos, límites, presupuestos, metas de ahorro
            e historial. No se puede deshacer. Si quieres una copia, descarga antes tus movimientos.
          </p>
          <div class="acciones">
            <button class="btn btn-outlined" @click="abrirEliminar">Eliminar mi cuenta</button>
          </div>
        </section>
      </template>
    </main>

    <!-- 3 · Confirmación honesta: consecuencias reales, botones iguales, sin culpa y un solo paso -->
    <AppDialog v-if="dialogoEliminar" titulo="¿Eliminar tu cuenta?" @cerrar="conservar">
      <div class="stack confirmacion">
        <template v-if="consecuencias.length">
          <p>Se borrarán para siempre:</p>
          <ul class="consecuencias">
            <li v-for="linea in consecuencias" :key="linea">{{ linea }}</li>
          </ul>
        </template>
        <p v-else>Tu cuenta todavía no tiene datos guardados.</p>
        <p>
          Ya no podrás iniciar sesión con <strong>{{ datos.cuenta.email }}</strong>. Esto no se puede deshacer.
        </p>
        <p v-if="resumen.movimientos > 0" class="copia">
          ¿Quieres guardar una copia antes?
          <button class="btn btn-text btn-small" @click="descargarCsv">
            <AppIcon name="download" :size="18" /> Descargar mis movimientos (CSV)
          </button>
        </p>
      </div>
      <template #acciones>
        <button class="btn btn-outlined" data-autofocus :disabled="eliminando" @click="conservar">
          Conservar mi cuenta
        </button>
        <button class="btn btn-outlined" :disabled="eliminando" @click="eliminar">
          Eliminar mi cuenta
        </button>
      </template>
    </AppDialog>
  </AppScaffold>
</template>

<style scoped>
.mis-datos {
  display: flex;
  flex-direction: column;
  gap: var(--space-m);
}

.bloque {
  display: flex;
  flex-direction: column;
  gap: var(--space-s);
  padding: var(--space-m);
}

.titulo-bloque {
  display: flex;
  align-items: center;
  gap: var(--space-s);
  margin: 0;
  font-size: var(--text-body-large, 18px);
}

.datos-cuenta {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: var(--space-xs) var(--space-m);
  margin: 0;
}

.datos-cuenta dt {
  color: var(--text-secondary);
}

.datos-cuenta dd {
  margin: 0;
  overflow-wrap: anywhere;
}

.resumen {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-s);
  margin: 0;
  padding: 0;
  list-style: none;
}

.resumen li {
  padding: 4px 12px;
  border: 1px solid var(--outline);
  border-radius: 8px;
}

.nota {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-caption);
}

.acciones {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-s);
}

.acciones .btn {
  white-space: normal;
}

.tabla-scroll {
  overflow-x: auto;
}

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-caption);
}

.tabla th,
.tabla td {
  padding: 6px 8px;
  border-bottom: 1px solid var(--gray-100);
  text-align: left;
  white-space: nowrap;
}

.tabla .num {
  text-align: right;
}

.lista-simple {
  margin: var(--space-s) 0 0;
  padding-left: var(--space-l);
}

.consecuencias {
  margin: 0;
  padding-left: var(--space-l);
}

.confirmacion p {
  margin: 0;
}

.copia {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-xs);
}
</style>
