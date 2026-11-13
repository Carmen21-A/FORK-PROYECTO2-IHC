// Tarea 9 (Parte A): cada flujo principal registra sus eventos y el panel /analitica los muestra como embudo.
// La semilla vacía la tabla eventos y deja a Martita con: ingreso de 300 Bs, gasto pendiente de 40 Bs
// (Pasaje de micro, Transporte), presupuesto de Transporte de 100 Bs y límite mensual de 500 Bs.
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { filaDe, iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
})

// Sale de lo que esté abierto y entra al panel
async function verPanel(page: Page) {
  await page.reload()
  await irDesdeElMenu(page, 'Analítica')
  await expect(page.getByRole('heading', { name: 'Embudos por flujo' })).toBeVisible()
}

const paso = (page: Page, evento: string) => page.getByTestId(`paso-${evento}`)

test('Registrar movimiento: inicio, error por monto vacío y éxito', async ({ page }) => {
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByRole('button', { name: 'Guardar' }).click() // sin monto
  await expect(page.getByText('El campo no puede estar vacío')).toBeVisible()
  await page.getByLabel('Monto (Bs)').fill('15')
  await page.getByLabel('Categoría', { exact: true }).selectOption('Comida')
  await page.getByRole('button', { name: 'Guardar' }).click()
  await expect(page.getByRole('status')).toContainText('Gasto registrado')

  await verPanel(page)
  await expect(paso(page, 'movimiento_iniciado')).toHaveText('1')
  await expect(paso(page, 'movimiento_guardado')).toHaveText('1')
  await expect(page.getByTestId('motivo-registrar-monto_vacio')).toContainText('1')
})

test('Aviso de presupuesto (Tarea 9): se muestra dos veces, se cancela una y se confirma otra', async ({ page }) => {
  for (const accion of ['Volver y ajustar', 'Guardar y exceder']) {
    await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
    await page.getByLabel('Categoría', { exact: true }).selectOption('Transporte')
    await page.getByLabel('Monto (Bs)').fill('80') // 40 + 80 = 120 de 100
    await page.getByRole('button', { name: 'Guardar' }).click()
    const aviso = page.getByRole('dialog', { name: 'Este gasto supera tu presupuesto' })
    await aviso.getByRole('button', { name: accion }).click()
    if (accion === 'Volver y ajustar') await page.reload()
  }
  await expect(page.getByRole('status')).toContainText('Gasto registrado')

  await verPanel(page)
  await expect(paso(page, 'aviso_presupuesto_mostrado')).toHaveText('2')
  await expect(paso(page, 'aviso_presupuesto_confirmado')).toHaveText('1')
  await expect(page.getByTestId('errores-aviso')).toHaveText('1') // un cancelado
})

test('Metas y fondos (Tarea 8) + pago rechazado: errores con motivo de lista fija', async ({ page }) => {
  // Crear meta: primero sin nombre (error), luego bien
  await irDesdeElMenu(page, 'Metas de Ahorro')
  await page.getByRole('button', { name: 'Nueva Meta' }).click()
  await page.getByLabel('Monto objetivo (Bs)').fill('500')
  await page.getByRole('button', { name: 'Crear meta' }).click()
  await expect(page.getByText('El nombre de la meta es obligatorio')).toBeVisible()
  await page.getByLabel('Nombre de la meta').fill('Matrícula')
  await page.getByRole('button', { name: 'Crear meta' }).click()
  const tarjeta = page.locator('.meta-card').filter({ hasText: 'Matrícula' })
  await expect(tarjeta).toBeVisible()

  // Asignar: primero sin fondos (300 disponibles, intenta 450), luego 280
  await tarjeta.getByRole('button', { name: 'Asignar fondos' }).click()
  await page.getByLabel(/Monto a asignar/i).fill('450')
  await expect(page.getByText(/Fondos insuficientes: el saldo disponible/)).toBeVisible()
  await page.getByRole('button', { name: 'Cancelar' }).click()
  await tarjeta.getByRole('button', { name: 'Asignar fondos' }).click()
  await page.getByLabel(/Monto a asignar/i).fill('280')
  await page.getByRole('button', { name: 'Confirmar asignación' }).click()
  await expect(tarjeta.getByText('280.0 Bs ahorrados de 500.0 Bs')).toBeVisible()

  // Pagar el pasaje de 40 Bs con solo 20 libres: permiso denegado
  await irDesdeElMenu(page, 'Movimientos')
  await filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pendiente' }).click()
  await expect(page.getByText(/reservados en tus metas/)).toBeVisible()

  await verPanel(page)
  await expect(paso(page, 'meta_creacion_iniciada')).toHaveText('1')
  await expect(paso(page, 'meta_creada')).toHaveText('1')
  await expect(page.getByTestId('motivo-meta-nombre_vacio')).toContainText('1')
  await expect(paso(page, 'fondos_operacion_iniciada')).toHaveText('2')
  await expect(paso(page, 'fondos_operacion_realizada')).toHaveText('1')
  await expect(page.getByTestId('motivo-fondos-fondos_insuficientes')).toContainText('1')
  await expect(paso(page, 'pago_iniciado')).toHaveText('1')
  await expect(paso(page, 'movimiento_pagado')).toHaveText('0')
  await expect(page.getByTestId('motivo-pagar-fondos_reservados_en_metas')).toContainText('1')
  // La mayor caída de la app se resalta con qué cambiaríamos
  await expect(page.getByTestId('mayor-caida')).toContainText('Qué cambiaríamos')
})

test('Pagar un pendiente: inicio y éxito', async ({ page }) => {
  await filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pendiente' }).click()
  await expect(filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pagado' })).toBeVisible()

  await verPanel(page)
  await expect(paso(page, 'pago_iniciado')).toHaveText('1')
  await expect(paso(page, 'movimiento_pagado')).toHaveText('1')
})

test('Presupuesto por categoría: error por letras y éxito', async ({ page }) => {
  await page.getByRole('button', { name: 'Presupuestos por Categoría' }).click()
  await page.getByRole('button', { name: 'Definir presupuesto de Comida' }).click()
  const dialogo = page.getByRole('dialog', { name: 'Presupuesto: Comida' })
  await dialogo.getByLabel('Monto mensual (Bs.)').fill('doscientos')
  await dialogo.getByRole('button', { name: 'Guardar' }).click()
  await expect(dialogo.getByText('No se permiten letras')).toBeVisible()
  await dialogo.getByLabel('Monto mensual (Bs.)').fill('200')
  await dialogo.getByRole('button', { name: 'Guardar' }).click()
  await expect(page.getByRole('status')).toContainText('Presupuesto para Comida actualizado')

  await verPanel(page)
  await expect(paso(page, 'presupuesto_edicion_iniciada')).toHaveText('1')
  await expect(paso(page, 'presupuesto_categoria_guardado')).toHaveText('1')
  await expect(page.getByTestId('motivo-presupuesto-letras')).toContainText('1')
  await expect(page.getByText('categoria: Comida · supera_limite: false')).toBeVisible()
})

test('Buscar: una búsqueda sin resultados se cuenta, sin guardar el texto buscado', async ({ page }) => {
  await page.getByLabel('Buscar por descripción').fill('pizza con amigos')
  await page.getByRole('button', { name: 'Buscar', exact: true }).click()
  await expect(page.getByText('pizza con amigos').first()).toBeVisible()

  await verPanel(page)
  await expect(page.getByTestId('busquedas-realizadas')).toHaveText('1')
  await expect(page.getByTestId('busquedas-sin-resultados')).toHaveText('1')
  await expect(page.getByText('pizza con amigos')).toHaveCount(0)
})
