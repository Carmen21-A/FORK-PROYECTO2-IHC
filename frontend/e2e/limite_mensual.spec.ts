// Limite mensual: Martita tiene 500 Bs de limite y lleva 40 Bs gastados
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
  await expect(page.getByText('Gastado: 40.0 Bs / Límite: 500.0 Bs')).toBeVisible()
})

async function cambiarLimite(page: Page, monto: string) {
  await page.getByRole('button', { name: 'Cambiar', exact: true }).click()
  const dialogo = page.getByRole('dialog', { name: 'Límite mensual de gastos' })
  await dialogo.getByLabel('Nuevo límite').fill(monto)
  await dialogo.getByRole('button', { name: 'Guardar' }).click()
}

test('Martita sube su límite y el disponible cambia', async ({ page }) => {
  await cambiarLimite(page, '800')

  await expect(page.getByRole('status')).toContainText('Límite actualizado')
  await expect(page.getByText('Gastado: 40.0 Bs / Límite: 800.0 Bs')).toBeVisible()
  await expect(page.getByText('Disponible: 760.0 Bs')).toBeVisible()
})

test('un límite menor a lo ya gastado no se acepta', async ({ page }) => {
  await cambiarLimite(page, '20')

  await expect(page.getByText('No puede ser menor a lo ya gastado "40.0 Bs"')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByText('Gastado: 40.0 Bs / Límite: 500.0 Bs')).toBeVisible()
})

test('con letras en el límite, le dice qué corregir', async ({ page }) => {
  await cambiarLimite(page, 'mil')

  await expect(page.getByText('No se permite letras, ingresa un número válido')).toBeVisible()
})
