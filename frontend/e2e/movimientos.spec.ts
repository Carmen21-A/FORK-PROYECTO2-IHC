// Movimientos: editar, eliminar, cambiar de estado, buscar y filtrar
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { filaDe, iniciarSesion, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
})

async function abrirOpcion(page: Page, descripcion: string, opcion: 'Editar' | 'Eliminar') {
  await filaDe(page, descripcion).getByRole('button', { name: 'Opciones' }).click()
  await page.getByRole('menuitem', { name: opcion }).click()
}

test.describe('Editar movimiento', () => {
  test('Martita corrige el monto de un gasto y el total cambia', async ({ page }) => {
    await abrirOpcion(page, 'Pasaje de micro', 'Editar')
    await expect(page.getByRole('dialog', { name: 'Editar movimiento' })).toBeVisible()
    await page.getByLabel('Monto (Bs)').fill('55')
    await page.getByRole('button', { name: 'Guardar' }).click()

    await expect(page.getByRole('status')).toContainText('Movimiento actualizado')
    await expect(page.getByText('Total gastos: 55.0 Bs')).toBeVisible()
    await expect(filaDe(page, 'Pasaje de micro')).toContainText('- 55 Bs')
  })

  test('un movimiento ya pagado no deja cambiar su monto', async ({ page }) => {
    await abrirOpcion(page, 'Mesada', 'Editar')

    await expect(page.getByLabel('Monto (Bs)')).toBeDisabled()
    await expect(page.getByText('No es posible modificar el monto porque el movimiento ya fue pagado')).toBeVisible()
  })
})

test.describe('Eliminar movimiento', () => {
  test('Martita elimina un gasto, lo confirma y el total baja', async ({ page }) => {
    await abrirOpcion(page, 'Pasaje de micro', 'Eliminar')
    const confirmar = page.getByRole('dialog', { name: 'Confirma que quieres eliminar este movimiento' })
    await confirmar.getByRole('button', { name: 'Eliminar' }).click()

    await expect(page.getByRole('status')).toContainText('Movimiento eliminado')
    await expect(page.getByText('Pasaje de micro')).toHaveCount(0)
    await expect(page.getByText('Total gastos: 0.0 Bs')).toBeVisible()
  })

  test('si cancela la confirmación, el gasto no se borra', async ({ page }) => {
    await abrirOpcion(page, 'Pasaje de micro', 'Eliminar')
    await page.getByRole('button', { name: 'Cancelar' }).click()

    await expect(filaDe(page, 'Pasaje de micro')).toBeVisible()
    await expect(page.getByText('Total gastos: 40.0 Bs')).toBeVisible()
  })
})

test.describe('Estados del movimiento', () => {
  test('Martita marca un gasto como pagado y luego lo cancela', async ({ page }) => {
    const fila = filaDe(page, 'Pasaje de micro')
    await fila.getByRole('button', { name: 'pendiente' }).click()
    await expect(fila.getByRole('button', { name: 'pagado' })).toBeVisible()

    // Cancelar es irreversible: pide confirmacion
    await fila.getByRole('button', { name: 'pagado' }).click()
    await page.getByRole('button', { name: 'Cancelar movimiento' }).click()

    await expect(fila.getByRole('button', { name: 'cancelado' })).toBeVisible()
    // Un gasto cancelado ya no cuenta
    await expect(page.getByText('Total gastos: 0.0 Bs')).toBeVisible()
    await expect(page.getByText('Gastado: 0.0 Bs')).toBeVisible()
  })

  test('si se arrepiente de cancelar, el gasto sigue pagado', async ({ page }) => {
    const fila = filaDe(page, 'Mesada')
    await fila.getByRole('button', { name: 'pagado' }).click()
    await page.getByRole('button', { name: 'Volver' }).click()

    await expect(fila.getByRole('button', { name: 'pagado' })).toBeVisible()
    await expect(page.getByText('Total ingresos: 300.0 Bs')).toBeVisible()
  })
})

test.describe('Buscar y filtrar', () => {
  test('Martita busca por descripción y filtra por ingresos', async ({ page }) => {
    await page.getByLabel('Buscar por descripción').fill('Pasaje')
    await page.getByRole('button', { name: 'Buscar', exact: true }).click()
    await expect(filaDe(page, 'Pasaje de micro')).toBeVisible()
    await expect(page.getByText('Mesada')).toHaveCount(0)

    await page.getByRole('button', { name: 'Quitar Buscar: Pasaje' }).click()
    await page.getByRole('button', { name: 'Ingresos' }).click()
    await expect(filaDe(page, 'Mesada')).toBeVisible()
    await expect(page.getByText('Pasaje de micro')).toHaveCount(0)
    await expect(page.getByText('Total gastos: 0.0 Bs · Total ingresos: 300.0 Bs')).toBeVisible()
  })

  test('sin resultados, se lo dice y puede quitar la búsqueda', async ({ page }) => {
    await page.getByLabel('Buscar por descripción').fill('zapatos')
    await page.getByRole('button', { name: 'Buscar', exact: true }).click()

    // Vacio: mensaje y accion
    await expect(page.getByText('No hay movimientos que coincidan con la búsqueda')).toBeVisible()
    await page.getByRole('button', { name: 'Quitar Buscar: zapatos' }).click()
    await expect(filaDe(page, 'Pasaje de micro')).toBeVisible()
  })
})
