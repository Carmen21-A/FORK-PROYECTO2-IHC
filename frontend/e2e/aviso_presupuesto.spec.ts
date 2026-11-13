// Tarea 9 (Parte B): Aviso antes de superar el límite de la categoría.
// La semilla deja a Martita con presupuesto de Transporte de 100 Bs y un gasto de 40 Bs (Pasaje de micro).
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
})

async function llenarGasto(page: Page, monto: string, descripcion: string) {
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Categoría', { exact: true }).selectOption('Transporte')
  await page.getByLabel('Monto (Bs)').fill(monto)
  await page.getByLabel('Descripción (opcional)').fill(descripcion)
  await page.getByRole('button', { name: 'Guardar' }).click()
}

const aviso = (page: Page) => page.getByRole('dialog', { name: 'Este gasto supera tu presupuesto' })

test('un gasto sin aviso, uno con aviso cancelado y otro confirmado que queda excedido', async ({ page }) => {
  // 1. Gasto SIN aviso: 40 + 30 = 70 de 100
  await llenarGasto(page, '30', 'Micro a la U')
  await expect(aviso(page)).toHaveCount(0)
  await expect(page.getByRole('status')).toContainText('Gasto registrado: 30.0 Bs')
  await expect(page.getByText('Total gastos: 70.0 Bs')).toBeVisible()

  // 2. Gasto CON aviso CANCELADO: 70 + 50 = 120 de 100 -> te pasarías 20 Bs
  await llenarGasto(page, '50', 'Taxi')
  await expect(aviso(page)).toBeVisible()
  await expect(aviso(page)).toContainText('te pasarías 20.0 Bs')
  await expect(aviso(page)).toContainText('Quedaría en')
  await expect(aviso(page)).toContainText('120.0 Bs')
  await aviso(page).getByRole('button', { name: 'Volver y ajustar' }).click()

  // Todo igual: no se guardó y el total no cambió
  await expect(aviso(page)).toHaveCount(0)
  await page.reload()
  await expect(page.getByText('Total gastos: 70.0 Bs')).toBeVisible()
  await expect(page.getByText('Taxi')).toHaveCount(0)

  // 3. Gasto CON aviso CONFIRMADO: se guarda y queda excedido
  await llenarGasto(page, '50', 'Taxi')
  await expect(aviso(page)).toBeVisible()
  await aviso(page).getByRole('button', { name: 'Guardar y exceder' }).click()
  await expect(page.getByRole('status')).toContainText('Gasto registrado: 50.0 Bs')
  await expect(page.getByText('Total gastos: 120.0 Bs')).toBeVisible()

  // Persistencia: el presupuesto de Transporte queda excedido tras recargar
  await page.reload()
  await irDesdeElMenu(page, 'Presupuesto por Categoría')
  const transporte = page.getByRole('article').filter({ has: page.getByRole('heading', { name: 'Transporte' }) })
  await expect(transporte).toContainText('Excedido por Bs. 20.00')
})

test('los ingresos no generan aviso', async ({ page }) => {
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Tipo', { exact: true }).selectOption('ingreso')
  await page.getByLabel('Categoría', { exact: true }).selectOption('Transporte')
  await page.getByLabel('Monto (Bs)').fill('500')
  await page.getByRole('button', { name: 'Guardar' }).click()

  await expect(aviso(page)).toHaveCount(0)
  await expect(page.getByRole('status')).toContainText('Ingreso registrado: 500.0 Bs')
})
