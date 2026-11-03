// Presupuesto por categoria: Martita tiene 100 Bs para Transporte y gasto 40 Bs en eso
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
  await page.getByRole('button', { name: 'Presupuestos por Categoría' }).click()
  await expect(page.getByRole('heading', { name: 'Presupuesto por Categoría' })).toBeVisible()
})

function tarjeta(page: Page, categoria: string) {
  return page.getByRole('article').filter({ has: page.getByRole('heading', { name: categoria }) })
}

async function definirPresupuesto(page: Page, categoria: string, monto: string) {
  await page.getByRole('button', { name: `Definir presupuesto de ${categoria}` }).click()
  const dialogo = page.getByRole('dialog', { name: `Presupuesto: ${categoria}` })
  await dialogo.getByLabel('Monto mensual (Bs.)').fill(monto)
  await dialogo.getByRole('button', { name: 'Guardar' }).click()
}

test('el gasto de Transporte cuenta en su presupuesto', async ({ page }) => {
  await expect(tarjeta(page, 'Transporte')).toContainText('En orden: 40% consumido')
  await expect(tarjeta(page, 'Transporte')).toContainText('Bs. 40.00')
})

test('Martita define un presupuesto para Comida y ve su estado', async ({ page }) => {
  await expect(tarjeta(page, 'Comida')).toContainText('Sin presupuesto fijado')

  await definirPresupuesto(page, 'Comida', '200')

  await expect(page.getByRole('status')).toContainText('Presupuesto para Comida actualizado a Bs. 200.00')
  await expect(tarjeta(page, 'Comida')).toContainText('En orden: 0% consumido')
  await expect(tarjeta(page, 'Comida')).toContainText('Bs. 200.00')
})

test('con letras en el monto, le dice qué corregir y no lo guarda', async ({ page }) => {
  await definirPresupuesto(page, 'Comida', 'doscientos')

  await expect(page.getByText('No se permiten letras, ingresa un número válido')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(tarjeta(page, 'Comida')).toContainText('Sin presupuesto fijado')
})

test('sin monto, le pide que lo escriba', async ({ page }) => {
  await definirPresupuesto(page, 'Comida', '')

  await expect(page.getByText('El presupuesto no debe estar vacío')).toBeVisible()
})
