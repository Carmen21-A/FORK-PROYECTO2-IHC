// Acceso y permisos: entrar, entrar sin sesion y salir
// (los errores al iniciar sesion estan en flujo_principal.spec.ts)
import { expect, test } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(() => sembrar())

test('Martita inicia sesión y llega a Movimientos', async ({ page }) => {
  await iniciarSesion(page, martita)

  await expect(page).toHaveURL(/\/movements$/)
  await expect(page.getByText('Total gastos: 40.0 Bs')).toBeVisible()
})

test('sin sesión, Movimientos lleva al login', async ({ page }) => {
  await page.goto('/movements')

  await expect(page).toHaveURL(/\/login$/)
  await expect(page.getByLabel('Correo electrónico')).toBeVisible()
})

test('sin sesión, Historial y Presupuesto por Categoría también llevan al login', async ({ page }) => {
  for (const ruta of ['/history', '/presupuestos-categoria', '/change-password']) {
    await page.goto(ruta)
    await expect(page, `ruta ${ruta}`).toHaveURL(/\/login$/)
  }
})

test('al cerrar sesión, vuelve al inicio y ya no puede ver Movimientos', async ({ page }) => {
  await iniciarSesion(page, martita)

  await irDesdeElMenu(page, 'Cerrar sesión')

  await expect(page.getByRole('heading', { name: /Bienvenido/ })).toBeVisible()
  await page.goto('/movements')
  await expect(page).toHaveURL(/\/login$/)
})

test('la sesión sigue abierta al recargar la página', async ({ page }) => {
  await iniciarSesion(page, martita)

  await page.reload()

  await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible()
  await expect(page.getByText('Pasaje de micro')).toBeVisible()
})
