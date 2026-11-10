<script setup>
// Pantalla de Metas de Ahorro y Gestión de Fondos Disponibles (Tarea 8)
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { MetasService } from '../services/metasService.js'
import {
  calcularPorcentajeMeta,
  diasRestantes,
  validarMontoOperacion,
} from '../utils/metas.js'
import { dartNum, parseDouble } from '../utils/formato.js'
import { showSnackBar } from '../widgets/snackbar.js'
import AppScaffold from '../widgets/AppScaffold.vue'
import AppDialog from '../widgets/AppDialog.vue'
import AppIcon from '../widgets/AppIcon.vue'

const router = useRouter()

const cargando = ref(true)
const metas = ref([])
const resumenFondos = ref({
  total_ingresos: 0,
  total_gastos: 0,
  saldo_total: 0,
  fondos_reservados: 0,
  saldo_disponible: 0,
})

// Modales
const dialogoCrear = ref(false)
const formMeta = ref({
  id: null,
  nombre: '',
  monto_objetivo: '',
  fecha_limite: '',
  error: null,
  guardando: false,
})

const dialogoOperacion = ref(null) // { tipo: 'asignar' | 'retirar' | 'transferir', meta: {...}, monto: '', destinoId: '', error: null, guardando: false }
const dialogoEliminar = ref(null) // meta a eliminar
const menuAbierto = ref(null)

onMounted(load)

async function load() {
  cargando.value = true
  try {
    const [listaMetas, fondos] = await Promise.all([
      MetasService.getAll(),
      MetasService.getResumenFondos(),
    ])
    metas.value = listaMetas
    resumenFondos.value = fondos
  } catch (e) {
    showSnackBar(e.message, 'var(--error-default)')
  } finally {
    cargando.value = false
  }
}

function abrirCrearMeta() {
  const hoyMas30 = new Date()
  hoyMas30.setDate(hoyMas30.getDate() + 30)
  const fechaDefecto = hoyMas30.toISOString().split('T')[0]

  formMeta.value = {
    id: null,
    nombre: '',
    monto_objetivo: '',
    fecha_limite: fechaDefecto,
    error: null,
    guardando: false,
  }
  dialogoCrear.value = true
}

function abrirEditarMeta(m) {
  formMeta.value = {
    id: m.id,
    nombre: m.nombre,
    monto_objetivo: String(m.monto_objetivo),
    fecha_limite: m.fecha_limite,
    error: null,
    guardando: false,
  }
  menuAbierto.value = null
  dialogoCrear.value = true
}

async function guardarMeta() {
  const f = formMeta.value
  if (!f.nombre.trim()) {
    f.error = 'El nombre de la meta es obligatorio'
    return
  }
  const obj = parseDouble(f.monto_objetivo)
  if (obj === null || obj <= 0) {
    f.error = 'El monto objetivo debe ser mayor a 0 Bs'
    return
  }
  if (!f.fecha_limite) {
    f.error = 'La fecha límite es obligatoria'
    return
  }

  f.guardando = true
  f.error = null
  try {
    if (f.id) {
      await MetasService.update(f.id, {
        nombre: f.nombre.trim(),
        monto_objetivo: obj,
        fecha_limite: f.fecha_limite,
      })
      showSnackBar('Meta de ahorro actualizada', 'var(--success-dark)')
    } else {
      await MetasService.create({
        nombre: f.nombre.trim(),
        monto_objetivo: obj,
        fecha_limite: f.fecha_limite,
      })
      showSnackBar('Meta de ahorro creada', 'var(--success-dark)')
    }
    dialogoCrear.value = false
    await load()
  } catch (e) {
    f.error = e.message
  } finally {
    f.guardando = false
  }
}

async function confirmarEliminar() {
  if (!dialogoEliminar.value) return
  const m = dialogoEliminar.value
  try {
    await MetasService.delete(m.id)
    showSnackBar(`Meta "${m.nombre}" eliminada`, 'var(--success-dark)')
    dialogoEliminar.value = null
    await load()
  } catch (e) {
    showSnackBar(e.message, 'var(--error-default)')
  }
}

// Operaciones de Fondos
function abrirAsignar(meta) {
  menuAbierto.value = null
  dialogoOperacion.value = {
    tipo: 'asignar',
    meta,
    monto: '',
    destinoId: '',
    error: null,
    guardando: false,
  }
}

function abrirRetirar(meta) {
  menuAbierto.value = null
  dialogoOperacion.value = {
    tipo: 'retirar',
    meta,
    monto: '',
    destinoId: '',
    error: null,
    guardando: false,
  }
}

function abrirTransferir(meta) {
  menuAbierto.value = null
  const otrasMetas = metas.value.filter((o) => o.id !== meta.id)
  dialogoOperacion.value = {
    tipo: 'transferir',
    meta,
    monto: '',
    destinoId: otrasMetas.length > 0 ? otrasMetas[0].id : '',
    error: null,
    guardando: false,
  }
}

const avisoValidacionOperacion = computed(() => {
  const op = dialogoOperacion.value
  if (!op || !op.monto) return null

  if (op.tipo === 'asignar') {
    return validarMontoOperacion(op.monto, resumenFondos.value.saldo_disponible, 'asignar')
  }
  if (op.tipo === 'retirar') {
    return validarMontoOperacion(op.monto, op.meta.monto_ahorrado, 'retirar')
  }
  if (op.tipo === 'transferir') {
    if (!op.destinoId) return 'Selecciona la meta de destino'
    return validarMontoOperacion(op.monto, op.meta.monto_ahorrado, 'transferir')
  }
  return null
})

async function ejecutarOperacion() {
  const op = dialogoOperacion.value
  if (!op || op.guardando) return

  const err = avisoValidacionOperacion.value
  if (err) {
    op.error = err
    return
  }

  const monto = parseDouble(op.monto)
  op.guardando = true
  op.error = null

  try {
    if (op.tipo === 'asignar') {
      await MetasService.asignar(op.meta.id, monto)
      showSnackBar(`Asignaste ${dartNum(monto)} Bs a "${op.meta.nombre}"`, 'var(--success-dark)')
    } else if (op.tipo === 'retirar') {
      await MetasService.retirar(op.meta.id, monto)
      showSnackBar(`Retiraste ${dartNum(monto)} Bs hacia el saldo disponible`, 'var(--success-dark)')
    } else if (op.tipo === 'transferir') {
      await MetasService.transferir(op.meta.id, op.destinoId, monto)
      showSnackBar(`Transferiste ${dartNum(monto)} Bs entre metas`, 'var(--success-dark)')
    }
    dialogoOperacion.value = null
    await load()
  } catch (e) {
    op.error = e.message
  } finally {
    op.guardando = false
  }
}

function alternarMenu(id) {
  menuAbierto.value = menuAbierto.value === id ? null : id
}
</script>

<template>
  <AppScaffold titulo="Metas de Ahorro" con-drawer>
    <template #acciones>
      <button class="btn btn-outlined btn-small" @click="abrirCrearMeta">
        <AppIcon name="add" :size="18" />
        Nueva Meta
      </button>
    </template>

    <main class="metas-screen">
      <!-- Navegación por Intención (Arquitectura de Información - Clase 20) -->
      <nav class="tabs-arquitectura" role="tablist" aria-label="Navegación por intención">
        <button
          type="button"
          role="tab"
          class="tab-item"
          @click="router.push('/movements')"
        >
          <AppIcon name="receipt_long" :size="18" />
          <span>Todos los movimientos</span>
        </button>

        <button
          type="button"
          role="tab"
          class="tab-item"
          @click="router.push('/movements')"
        >
          <AppIcon name="schedule" :size="18" />
          <span>Por pagar</span>
        </button>

        <button
          type="button"
          role="tab"
          class="tab-item"
          @click="router.push('/presupuestos-categoria')"
        >
          <AppIcon name="pie_chart" :size="18" />
          <span>Presupuestos</span>
        </button>

        <button
          type="button"
          role="tab"
          class="tab-item activa"
          aria-selected="true"
        >
          <AppIcon name="savings" :size="18" />
          <span>Metas</span>
        </button>
      </nav>

      <!-- Panel de Resumen Financiero y Fondos Disponibles -->
      <section class="card balance-card">
        <div class="balance-item">
          <span class="balance-label">Saldo Total</span>
          <strong class="balance-valor valor-total">
            {{ dartNum(resumenFondos.saldo_total) }} Bs
          </strong>
          <span class="balance-sub">Ingresos - Gastos</span>
        </div>

        <div class="balance-divisor" />

        <div class="balance-item">
          <span class="balance-label">Fondos en Metas</span>
          <strong class="balance-valor valor-reservado">
            {{ dartNum(resumenFondos.fondos_reservados) }} Bs
          </strong>
          <span class="balance-sub">Dinero protegido</span>
        </div>

        <div class="balance-divisor" />

        <div class="balance-item">
          <span class="balance-label">Saldo Disponible</span>
          <strong
            class="balance-valor valor-disponible"
            :class="{ 'alerta-bajo': resumenFondos.saldo_disponible <= 0 }"
          >
            {{ dartNum(resumenFondos.saldo_disponible) }} Bs
          </strong>
          <span class="balance-sub">Libre para asignar</span>
        </div>
      </section>

      <!-- Banner explicativo de reglas de negocio (Tarea 8) -->
      <div class="banner-regla">
        <AppIcon name="info" :size="18" color="var(--primary-300)" />
        <span>
          <strong>Metas con fondos disponibles:</strong> Apartar dinero para tus metas reduce tu
          saldo disponible para proteger tus ahorros, sin crear gastos ficticios.
        </span>
      </div>

      <!-- Estado de carga -->
      <div v-if="cargando" class="vacio">Cargando metas de ahorro...</div>

      <!-- Estado vacío cuando no hay metas -->
      <section v-else-if="metas.length === 0" class="card vacio vacio-accion">
        <AppIcon name="savings" :size="48" color="var(--primary-base)" />
        <h3>Aún no tienes metas de ahorro</h3>
        <p>Crea tu primera meta con un monto objetivo y fecha para empezar a apartar fondos.</p>
        <button class="btn btn-elevated" @click="abrirCrearMeta">
          <AppIcon name="add" :size="18" />
          Crear mi primera meta
        </button>
      </section>

      <!-- Listado de Metas de Ahorro -->
      <section v-else class="grid-metas">
        <article v-for="m in metas" :key="m.id" class="card meta-card">
          <header class="meta-header">
            <div>
              <h2 class="meta-titulo">{{ m.nombre }}</h2>
              <span class="meta-fecha">
                Fecha límite: {{ m.fecha_limite }}
                <template v-if="diasRestantes(m.fecha_limite) !== null">
                  ·
                  {{
                    diasRestantes(m.fecha_limite) > 0
                      ? `${diasRestantes(m.fecha_limite)} días restantes`
                      : 'Vencida'
                  }}
                </template>
              </span>
            </div>

            <div class="menu-wrap">
              <button
                class="icon-btn"
                title="Opciones de meta"
                aria-label="Opciones"
                @click.stop="alternarMenu(m.id)"
              >
                <AppIcon name="more_vert" />
              </button>
              <div v-if="menuAbierto === m.id" class="menu" role="menu">
                <button class="menu-item" role="menuitem" @click="abrirEditarMeta(m)">
                  <AppIcon name="edit" :size="18" />
                  Editar
                </button>
                <button
                  class="menu-item"
                  role="menuitem"
                  style="color: var(--error-default)"
                  @click="dialogoEliminar = m; menuAbierto = null"
                >
                  <AppIcon name="delete" :size="18" />
                  Eliminar
                </button>
              </div>
            </div>
          </header>

          <!-- Barra de Progreso -->
          <div class="progreso-contenedor">
            <div class="progreso-barra">
              <div
                class="progreso-relleno"
                :style="{
                  width: `${calcularPorcentajeMeta(m.monto_ahorrado, m.monto_objetivo)}%`,
                  backgroundColor: m.cumplida ? 'var(--success-default)' : 'var(--primary-base)',
                }"
              />
            </div>
            <div class="progreso-valores">
              <span>
                <strong>{{ dartNum(m.monto_ahorrado) }} Bs</strong> ahorrados de
                {{ dartNum(m.monto_objetivo) }} Bs
              </span>
              <strong
                class="porcentaje"
                :style="{ color: m.cumplida ? 'var(--success-dark)' : 'var(--text-primary)' }"
              >
                {{ calcularPorcentajeMeta(m.monto_ahorrado, m.monto_objetivo) }}%
              </strong>
            </div>
          </div>

          <div v-if="m.cumplida" class="badge-cumplida">
            <AppIcon name="check_circle" :size="16" color="var(--success-dark)" />
            <span>¡Meta completada con éxito!</span>
          </div>

          <!-- Acciones de Fondos -->
          <footer class="meta-acciones">
            <button
              class="btn btn-elevated btn-small btn-asignar"
              title="Asignar dinero del disponible"
              @click="abrirAsignar(m)"
            >
              <AppIcon name="add" :size="16" />
              Asignar fondos
            </button>

            <button
              v-if="m.monto_ahorrado > 0 && metas.length > 1"
              class="btn btn-outlined btn-small"
              title="Transferir a otra meta"
              @click="abrirTransferir(m)"
            >
              <AppIcon name="swap_horiz" :size="16" />
              Transferir
            </button>

            <button
              v-if="m.monto_ahorrado > 0"
              class="btn btn-outlined btn-small"
              title="Devolver al saldo disponible"
              @click="abrirRetirar(m)"
            >
              <AppIcon name="arrow_downward" :size="16" />
              Retirar
            </button>
          </footer>
        </article>
      </section>
    </main>

    <!-- Diálogo Crear / Editar Meta -->
    <AppDialog
      v-if="dialogoCrear"
      :titulo="formMeta.id ? 'Editar meta de ahorro' : 'Nueva meta de ahorro'"
      @cerrar="dialogoCrear = false"
    >
      <form class="stack" @submit.prevent="guardarMeta">
        <label class="field">
          <span>Nombre de la meta</span>
          <input
            v-model="formMeta.nombre"
            class="input"
            type="text"
            placeholder="Ej. Laptop para la universidad"
            required
          />
        </label>

        <label class="field">
          <span>Monto objetivo (Bs)</span>
          <input
            v-model="formMeta.monto_objetivo"
            class="input"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="Ej. 1500"
            required
          />
        </label>

        <label class="field">
          <span>Fecha límite</span>
          <input
            v-model="formMeta.fecha_limite"
            class="input"
            type="date"
            required
          />
        </label>

        <div v-if="formMeta.error" class="error-banner">
          {{ formMeta.error }}
        </div>

        <div class="row modal-acciones">
          <button type="button" class="btn btn-outlined" @click="dialogoCrear = false">
            Cancelar
          </button>
          <button type="submit" class="btn btn-elevated" :disabled="formMeta.guardando">
            {{ formMeta.guardando ? 'Guardando...' : formMeta.id ? 'Actualizar' : 'Crear meta' }}
          </button>
        </div>
      </form>
    </AppDialog>

    <!-- Diálogo Operación: Asignar / Retirar / Transferir -->
    <AppDialog
      v-if="dialogoOperacion"
      :titulo="
        dialogoOperacion.tipo === 'asignar'
          ? `Asignar fondos a '${dialogoOperacion.meta.nombre}'`
          : dialogoOperacion.tipo === 'retirar'
          ? `Retirar fondos de '${dialogoOperacion.meta.nombre}'`
          : `Transferir desde '${dialogoOperacion.meta.nombre}'`
      "
      @cerrar="dialogoOperacion = null"
    >
      <form class="stack" @submit.prevent="ejecutarOperacion">
        <!-- Info contextual -->
        <div v-if="dialogoOperacion.tipo === 'asignar'" class="info-operacion">
          <span>Saldo disponible actual:</span>
          <strong>{{ dartNum(resumenFondos.saldo_disponible) }} Bs</strong>
        </div>

        <div v-if="dialogoOperacion.tipo === 'retirar'" class="info-operacion">
          <span>Monto ahorrado en la meta:</span>
          <strong>{{ dartNum(dialogoOperacion.meta.monto_ahorrado) }} Bs</strong>
        </div>

        <!-- Selector de Meta Destino para Transferencias -->
        <label v-if="dialogoOperacion.tipo === 'transferir'" class="field">
          <span>Meta de destino</span>
          <select v-model="dialogoOperacion.destinoId" class="select" required>
            <option
              v-for="d in metas.filter((m) => m.id !== dialogoOperacion.meta.id)"
              :key="d.id"
              :value="d.id"
            >
              {{ d.nombre }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>Monto a {{ dialogoOperacion.tipo }} (Bs)</span>
          <input
            v-model="dialogoOperacion.monto"
            class="input"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="0.00"
            required
            autofocus
          />
        </label>

        <!-- Aviso en vivo de validación -->
        <div v-if="avisoValidacionOperacion" class="error-banner">
          {{ avisoValidacionOperacion }}
        </div>
        <div v-else-if="dialogoOperacion.error" class="error-banner">
          {{ dialogoOperacion.error }}
        </div>

        <div class="row modal-acciones">
          <button type="button" class="btn btn-outlined" @click="dialogoOperacion = null">
            Cancelar
          </button>
          <button
            type="submit"
            class="btn btn-elevated"
            :disabled="dialogoOperacion.guardando || !!avisoValidacionOperacion"
          >
            {{
              dialogoOperacion.guardando
                ? 'Procesando...'
                : dialogoOperacion.tipo === 'asignar'
                ? 'Confirmar asignación'
                : dialogoOperacion.tipo === 'retirar'
                ? 'Confirmar retiro'
                : 'Confirmar transferencia'
            }}
          </button>
        </div>
      </form>
    </AppDialog>

    <!-- Diálogo Confirmar Eliminación -->
    <AppDialog
      v-if="dialogoEliminar"
      titulo="¿Eliminar meta de ahorro?"
      @cerrar="dialogoEliminar = null"
    >
      <div class="stack">
        <p>
          ¿Seguro que deseas eliminar la meta <strong>"{{ dialogoEliminar.nombre }}"</strong>?
        </p>
        <p v-if="dialogoEliminar.monto_ahorrado > 0" class="aviso-liberacion">
          💡 Sus fondos ahorrados de
          <strong>{{ dartNum(dialogoEliminar.monto_ahorrado) }} Bs</strong> se liberarán y volverán
          automáticamente a tu saldo disponible.
        </p>
        <div class="row modal-acciones">
          <button class="btn btn-outlined" @click="dialogoEliminar = null">Cancelar</button>
          <button class="btn btn-elevated btn-danger" @click="confirmarEliminar">
            Eliminar meta
          </button>
        </div>
      </div>
    </AppDialog>
  </AppScaffold>
</template>

<style scoped>
.metas-screen {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-m);
}

/* Tarjeta de Balance y Saldos */
.balance-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: var(--space-l);
  margin-bottom: var(--space-m);
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  border-radius: 14px;
}

.balance-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  text-align: center;
}

.balance-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary, #64748b);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.balance-valor {
  font-size: 22px;
  font-weight: 800;
}

.valor-total {
  color: var(--text-primary, #0f172a);
}

.valor-reservado {
  color: var(--primary-400, #bc8244);
}

.valor-disponible {
  color: var(--success-dark, #15803d);
}

.valor-disponible.alerta-bajo {
  color: var(--error-default, #ef4444);
}

.balance-sub {
  font-size: 12px;
  color: var(--text-secondary, #94a3b8);
}

.balance-divisor {
  width: 1px;
  height: 48px;
  background: var(--gray-200, #e2e8f0);
}

/* Banner explicativo */
.banner-regla {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(237, 165, 88, 0.12);
  border: 1px solid rgba(237, 165, 88, 0.3);
  border-radius: 10px;
  margin-bottom: var(--space-l);
  font-size: 13px;
  color: #5c3810;
}

/* Grid de Metas */
.grid-metas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: var(--space-m);
}

.meta-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-m);
  padding: var(--space-l);
  border-radius: 14px;
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.meta-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.meta-titulo {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #0f172a);
}

.meta-fecha {
  font-size: 12px;
  color: var(--text-secondary, #64748b);
}

/* Barra de progreso */
.progreso-contenedor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progreso-barra {
  width: 100%;
  height: 12px;
  background: var(--gray-100, #f1f5f9);
  border-radius: 6px;
  overflow: hidden;
}

.progreso-relleno {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 6px;
}

.progreso-valores {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-secondary, #475569);
}

.badge-cumplida {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  background: var(--success-light, #dcfce7);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: var(--success-dark, #15803d);
}

.meta-acciones {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-top: var(--space-s);
  border-top: 1px solid var(--gray-100, #f1f5f9);
}

/* Diálogos y Modales */
.info-operacion {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--gray-100, #f8fafc);
  border-radius: 8px;
  font-size: 14px;
}

.error-banner {
  padding: 8px 12px;
  background: var(--error-light, #fee2e2);
  color: var(--error-dark, #b91c1c);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
}

.modal-acciones {
  justify-content: flex-end;
  gap: var(--space-s);
  margin-top: var(--space-m);
}

.btn-danger {
  background: var(--error-default, #ef4444);
  color: white;
}

.aviso-liberacion {
  font-size: 13px;
  color: var(--primary-500, #61411f);
}

/* Tabs Arquitectura */
.tabs-arquitectura {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: 6px;
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--gray-200, #e2e8f0);
  border-radius: 12px;
  margin-bottom: var(--space-m);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.tab-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1;
  padding: 10px 14px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary, #64748b);
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-item:hover {
  background: rgba(237, 165, 88, 0.12);
  color: var(--text-primary, #1e293b);
}

.tab-item.activa {
  background: var(--primary-base, #eda558);
  color: #1a0e04;
  font-weight: 700;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.menu-wrap {
  position: relative;
}

@media (max-width: 600px) {
  .balance-card {
    flex-direction: column;
    gap: var(--space-m);
  }
  .balance-divisor {
    display: none;
  }
  .grid-metas {
    grid-template-columns: 1fr;
  }
}
</style>
