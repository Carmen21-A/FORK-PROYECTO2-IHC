// Historial: cada accion sobre un movimiento queda registrada
import { expect, test } from '@playwright/test'
import { sembrar } from './semilla.js'
import { filaDe, iniciarSesion, irDesdeElMenu, martita, pablo } from './usuarios.js'

test.beforeEach(() => sembrar())

test('lo que hace Martita aparece en su historial', async ({ page }) => {
  await iniciarSesion(page, martita)
  await filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pendiente' }).click()
  await expect(filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pagado' })).toBeVisible()

  await irDesdeElMenu(page, 'Historial')

  await expect(page.getByRole('heading', { name: 'Historial' })).toBeVisible()
  await expect(filaDe(page, 'Estado cambiado')).toContainText('Estado cambiado a pagado')
  await expect(filaDe(page, 'Gasto 40 Bs · Transporte · Pasaje de micro')).toContainText('Movimiento creado')
})

test('Martita busca en su historial; sin resultados, se lo dice', async ({ page }) => {
  await iniciarSesion(page, martita)
  await irDesdeElMenu(page, 'Historial')

  await page.getByLabel('Buscar en el historial').fill('Mesada')
  await expect(filaDe(page, 'Mesada')).toBeVisible()
  await expect(page.getByText('Pasaje de micro')).toHaveCount(0)

  await page.getByLabel('Buscar en el historial').fill('zapatos')
  await expect(page.getByText('Sin resultados para "zapatos"')).toBeVisible()
})

test('Pablo no tiene historial y sabe cómo empezar', async ({ page }) => {
  await iniciarSesion(page, pablo)
  await irDesdeElMenu(page, 'Historial')

  // Vacio: mensaje y accion
  await expect(page.getByText('Aún no hay movimientos registrados')).toBeVisible()
  await page.getByRole('button', { name: 'Registrar movimiento' }).click()
  await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible()
})
