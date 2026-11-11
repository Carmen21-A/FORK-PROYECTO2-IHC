// Clase 21 - Analítica de interacción: dos eventos, un panel, una decisión.
// La semilla vacía la tabla eventos: cada prueba empieza en 0.
import { expect, test } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
})

test('Martita empieza dos movimientos, guarda uno y el panel muestra 2, 1 y 50 %', async ({ page }) => {
  // 1. Empieza un movimiento y lo abandona (recarga la página sin guardar)
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await expect(page.getByLabel('Monto (Bs)')).toBeVisible()
  await page.reload()

  // 2. Empieza otro y lo guarda
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Categoría', { exact: true }).selectOption('Comida')
  await page.getByLabel('Monto (Bs)').fill('25.5')
  await page.getByLabel('Descripción (opcional)').fill('Almuerzo con Ana')
  await page.getByRole('button', { name: 'Guardar' }).click()
  await expect(page.getByRole('status')).toContainText('Gasto registrado')

  // 3. El panel /analitica cuenta los eventos
  await irDesdeElMenu(page, 'Analítica')
  await expect(page.getByTestId('total-iniciados')).toHaveText('2')
  await expect(page.getByTestId('total-guardados')).toHaveText('1')
  await expect(page.getByTestId('porcentaje-terminan')).toHaveText('50 %')
  await expect(page.getByText('tipo: gasto · categoria: Comida')).toBeVisible()

  // 4. Privacidad: no viajó la descripción ni el monto
  await expect(page.getByText('Almuerzo con Ana')).toHaveCount(0)
  await expect(page.getByText('25.5')).toHaveCount(0)

  // 5. Persistencia: los eventos siguen al recargar
  await page.reload()
  await expect(page.getByTestId('total-guardados')).toHaveText('1')
})

test('si el guardado falla, cuenta como iniciado pero no como guardado', async ({ page }) => {
  // Martita tiene un límite de 500 Bs y ya gastó 40: un gasto de 600 Bs no se guarda
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Monto (Bs)').fill('600')
  await page.getByRole('button', { name: 'Guardar' }).click()
  await expect(page.getByRole('status')).toContainText('supera tu límite mensual')

  // Se rinde: sale sin guardar
  await page.reload()
  await irDesdeElMenu(page, 'Analítica')
  await expect(page.getByTestId('total-iniciados')).toHaveText('1')
  await expect(page.getByTestId('total-guardados')).toHaveText('0')
  await expect(page.getByTestId('porcentaje-terminan')).toHaveText('0 %')
})
