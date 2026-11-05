// Tarea 6 - Feature "Recurrentes": gasto semanal o mensual; al pagarlo se genera la
// siguiente ocurrencia y cuenta en el presupuesto.
// La prueba comprueba: aparece la proxima ocurrencia y el consumo sube.
// Semilla: Martita tiene un limite de 500 Bs y lleva 40 Bs gastados ("Pasaje de micro").
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { filaDe, iniciarSesion, martita } from './usuarios.js'

const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
  'septiembre', 'octubre', 'noviembre', 'diciembre']

// El gasto se registra el dia 1 del mes actual: asi "+7 dias" cae siempre en el mismo mes
const hoy = new Date()
const dia1 = new Date(hoy.getFullYear(), hoy.getMonth(), 1)
const dia8 = new Date(hoy.getFullYear(), hoy.getMonth(), 8)
const mesSiguiente = new Date(hoy.getFullYear(), hoy.getMonth() + 1, 1)

const texto = (f: Date) => `${f.getDate()} de ${MESES[f.getMonth()]}`
const iso = (f: Date) =>
  `${f.getFullYear()}-${String(f.getMonth() + 1).padStart(2, '0')}-${String(f.getDate()).padStart(2, '0')}`

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
  await expect(page.getByText('Gastado: 40.0 Bs / Límite: 500.0 Bs')).toBeVisible()
})

async function registrarGastoRecurrente(page: Page, monto: string, repetir: 'Cada semana' | 'Cada mes') {
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Categoría', { exact: true }).selectOption('Comida')
  await page.getByLabel('Repetir').selectOption({ label: repetir })
  await page.getByLabel('Fecha del movimiento').fill(iso(dia1))
  await page.getByLabel('Monto (Bs)').fill(monto)
  await page.getByLabel('Descripción (opcional)').fill('Pensión')
  await page.getByRole('button', { name: 'Guardar' }).click()
  await expect(page.getByRole('status')).toContainText('Gasto registrado')
}

// La fila del gasto "Pensión" de una fecha (hay una por cada ocurrencia)
const pension = (page: Page, fecha: Date) => filaDe(page, `Categoría: Comida · ${texto(fecha)} · Descripción: Pensión`)

// ============================================================================
// CAMINO FELIZ
// ============================================================================
test('Martita paga un gasto semanal: aparece el de la próxima semana y el consumo sube', async ({ page }) => {
  await registrarGastoRecurrente(page, '30', 'Cada semana')

  // Antes de pagarlo ya se ve cuando sera la proxima
  await expect(pension(page, dia1)).toContainText(`Se repite cada semana · próxima: ${texto(dia8)}`)
  await expect(page.getByText('Gastado: 70.0 Bs')).toBeVisible()

  await pension(page, dia1).getByRole('button', { name: 'pendiente' }).click()

  // Aparece la proxima ocurrencia, pendiente
  await expect(page.getByRole('status')).toContainText(`Se generó el próximo gasto: ${texto(dia8)}`)
  await expect(pension(page, dia8).getByRole('button', { name: 'pendiente' })).toBeVisible()
  await expect(pension(page, dia1).getByRole('button', { name: 'pagado' })).toBeVisible()

  // El consumo sube: 40 + 30 + 30
  await expect(page.getByText('Gastado: 100.0 Bs / Límite: 500.0 Bs')).toBeVisible()

  // Y cuenta en el presupuesto por categoria
  await page.getByRole('button', { name: 'Presupuestos por Categoría' }).click()
  const comida = page.getByRole('article').filter({ has: page.getByRole('heading', { name: 'Comida' }) })
  await expect(comida).toContainText('Consumido (2 gastos)')
  await expect(comida).toContainText('Bs. 60.00')
})

test('Martita paga un gasto mensual: aparece el del próximo mes y cuenta en ese mes', async ({ page }) => {
  await registrarGastoRecurrente(page, '30', 'Cada mes')
  await expect(pension(page, dia1)).toContainText(`Se repite cada mes · próxima: ${texto(mesSiguiente)}`)

  await pension(page, dia1).getByRole('button', { name: 'pendiente' }).click()

  await expect(page.getByRole('status')).toContainText(`Se generó el próximo gasto: ${texto(mesSiguiente)}`)
  await expect(pension(page, mesSiguiente)).toBeVisible()
  // El total de todos los gastos sube (40 + 30 + 30); el del mes actual solo suma el primero
  await expect(page.getByText('Total gastos: 100.0 Bs')).toBeVisible()
  await expect(page.getByText('Gastado: 70.0 Bs')).toBeVisible()

  // En el presupuesto del mes siguiente ya aparece el gasto
  await page.getByRole('button', { name: 'Presupuestos por Categoría' }).click()
  await page.getByRole('button', { name: 'Mes siguiente' }).click()
  const comida = page.getByRole('article').filter({ has: page.getByRole('heading', { name: 'Comida' }) })
  await expect(comida).toContainText('Consumido (1 gastos)')
  await expect(comida).toContainText('Bs. 30.00')
})

// ============================================================================
// CAMINOS ALTERNATIVOS
// ============================================================================
test('si el próximo gasto supera el límite, no se genera y se lo explica', async ({ page }) => {
  await registrarGastoRecurrente(page, '250', 'Cada semana')
  await expect(page.getByText('Gastado: 290.0 Bs')).toBeVisible()

  await pension(page, dia1).getByRole('button', { name: 'pendiente' }).click()

  // 290 + 250 = 540 > 500: no se genera
  await expect(page.getByRole('status')).toContainText('No se generó el gasto')
  await expect(page.getByRole('status')).toContainText('supera tu límite mensual')
  await expect(filaDe(page, 'Pensión')).toHaveCount(1)
  await expect(page.getByText('Gastado: 290.0 Bs')).toBeVisible()
})

test('un gasto que no se repite, al pagarlo, no genera otro', async ({ page }) => {
  await filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pendiente' }).click()

  await expect(filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pagado' })).toBeVisible()
  await expect(filaDe(page, 'Pasaje de micro')).toHaveCount(1)
  await expect(page.getByText('Gastado: 40.0 Bs')).toBeVisible()
})

test('un ingreso no ofrece la opción de repetir', async ({ page }) => {
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await expect(page.getByLabel('Repetir')).toBeVisible()

  await page.getByLabel('Tipo').selectOption('ingreso')

  await expect(page.getByLabel('Repetir')).toHaveCount(0)
})
