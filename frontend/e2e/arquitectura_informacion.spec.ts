// Prueba E2E: Arquitectura de Información (Clase 20)
// Verifica la navegación por intención: pestañas Por pagar, Movimientos y Presupuestos
import { expect, test } from '@playwright/test'
import { sembrar } from './semilla.js'
import { filaDe, iniciarSesion, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
})

test('Navegación por intención: filtrar pendientes, saldarlos y verificar consistencia de estados', async ({
  page,
}) => {
  // 1. En la pestaña por defecto (Todos los movimientos) se ven todos
  await expect(page.getByRole('tab', { name: 'Todos los movimientos' })).toBeVisible()
  await expect(page.getByRole('tab', { name: /Por pagar/ })).toBeVisible()
  await expect(page.getByRole('tab', { name: 'Presupuestos' })).toBeVisible()

  await expect(filaDe(page, 'Pasaje de micro')).toBeVisible()
  await expect(filaDe(page, 'Mesada')).toBeVisible()

  // 2. Cambiar a la pestaña "Por pagar"
  await page.getByRole('tab', { name: /Por pagar/ }).click()

  // Muestra el resumen de urgencia y solo los pendientes
  await expect(page.getByText('Por pagar este mes: 40.0 Bs')).toBeVisible()
  await expect(filaDe(page, 'Pasaje de micro')).toBeVisible()
  await expect(page.getByText('Mesada')).toHaveCount(0)

  // 3. Saldar el gasto pendiente directamente
  const filaPasaje = filaDe(page, 'Pasaje de micro')
  await filaPasaje.getByRole('button', { name: 'pendiente' }).click()

  // 4. Al saldarlo, desaparece de "Por pagar" y se muestra el estado vacío motivacional
  await expect(page.getByText(/¡Excelente! No tienes pagos pendientes por saldar/)).toBeVisible()
  await expect(page.getByText('Mesada')).toHaveCount(0)

  // 5. Al regresar a "Todos los movimientos", el ítem aparece como pagado (consistencia de estados)
  await page.getByRole('tab', { name: 'Todos los movimientos' }).click()
  await expect(filaDe(page, 'Pasaje de micro')).toBeVisible()
  await expect(filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pagado' })).toBeVisible()
  await expect(filaDe(page, 'Mesada')).toBeVisible()

  // 6. Al pulsar la pestaña Presupuestos, navega al control de categorías
  await page.getByRole('tab', { name: 'Presupuestos' }).click()
  await expect(page).toHaveURL(/.*presupuestos-categoria/)
})

