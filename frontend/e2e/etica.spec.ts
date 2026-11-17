// Clase 22 · Patrones oscuros: el aviso de presupuesto no empuja a pasarse.
// La semilla deja a Martita con presupuesto de Transporte de 100 Bs y un gasto de 40 Bs (Pasaje de micro).
import { expect, test, type Locator } from '@playwright/test'
import { sembrar } from './semilla.js'
import { filaDe, iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
})

test('el aviso de presupuesto muestra las dos opciones iguales y sin culpa', async ({ page }) => {
  // Un gasto de 80 Bs: 40 + 80 = 120 de 100 -> aparece el aviso
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Categoría', { exact: true }).selectOption('Transporte')
  await page.getByLabel('Monto (Bs)').fill('80')
  await page.getByRole('button', { name: 'Guardar' }).click()

  const aviso = page.getByRole('dialog', { name: 'Este gasto supera tu presupuesto' })
  await expect(aviso).toBeVisible()

  // Evidencia (opcional): FOTO_CLASE22=antes|despues guarda la captura del aviso
  if (process.env.FOTO_CLASE22) {
    await aviso.screenshot({ path: `../evidencias/clase-22/${process.env.FOTO_CLASE22}.png` })
  }

  // La consecuencia se dice con el número exacto
  await expect(aviso).toContainText('te pasarías 20.0 Bs')

  // Las dos salidas tienen el mismo peso visual: ninguna se destaca sobre la otra
  const botones = aviso.getByRole('button')
  await expect(botones).toHaveCount(2)
  const [claseVolver, claseGuardar] = await botones.evaluateAll((bs) => bs.map((b) => b.className))
  expect(claseGuardar).toBe(claseVolver)

  // Los botones dicen lo que hacen, sin reproche («de todas formas»)
  await expect(aviso.getByRole('button', { name: 'Volver y ajustar' })).toBeVisible()
  await expect(aviso.getByRole('button', { name: 'Guardar y exceder' })).toBeVisible()
  await expect(aviso).not.toContainText('de todas formas')

  // La opción segura sigue recibiendo el foco al abrir el aviso
  await expect(aviso.getByRole('button', { name: 'Volver y ajustar' })).toBeFocused()
})

// ---------- Tarea 10 · Revisión de los seis patrones en toda la app ----------
// Patrón 2 (confirmaciones engañosas): en cada confirmación de algo irreversible, las dos
// opciones tienen el mismo estilo, dicen lo que hacen y la salida segura recibe el foco.
async function esperarBotonesIguales(dialogo: Locator, seguro: string, destructivo: string) {
  await expect(dialogo).toBeVisible()
  const botonSeguro = dialogo.getByRole('button', { name: seguro, exact: true })
  const botonDestructivo = dialogo.getByRole('button', { name: destructivo, exact: true })
  await expect(botonSeguro).toBeVisible()
  await expect(botonDestructivo).toBeVisible()
  expect(await botonDestructivo.getAttribute('class')).toBe(await botonSeguro.getAttribute('class'))
  await expect(botonSeguro).toBeFocused()
  await botonSeguro.click()
  await expect(dialogo).toBeHidden()
}

test('eliminar un movimiento: botones iguales y la consecuencia explicada', async ({ page }) => {
  await filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'Opciones' }).click()
  await page.getByRole('menuitem', { name: 'Eliminar' }).click()
  const dialogo = page.getByRole('dialog', { name: 'Confirma que quieres eliminar este movimiento' })
  await expect(dialogo).toContainText('desaparecerá de tu lista y de tus totales')
  await esperarBotonesIguales(dialogo, 'Conservar movimiento', 'Eliminar movimiento')
  await expect(filaDe(page, 'Pasaje de micro')).toBeVisible()
})

test('cancelar un movimiento: la acción irreversible no es el botón destacado', async ({ page }) => {
  await filaDe(page, 'Mesada').getByRole('button', { name: 'pagado' }).click()
  const dialogo = page.getByRole('dialog', { name: 'Confirmar cancelación' })
  await expect(dialogo).toContainText('dejará de contar en tus totales')
  await esperarBotonesIguales(dialogo, 'Volver', 'Cancelar movimiento')
})

test('eliminar un presupuesto por categoría: botones iguales', async ({ page }) => {
  await irDesdeElMenu(page, 'Presupuesto por Categoría')
  await page.getByRole('button', { name: 'Eliminar presupuesto de Transporte' }).click()
  const dialogo = page.getByRole('dialog', { name: 'Eliminar presupuesto de Transporte' })
  await esperarBotonesIguales(dialogo, 'Conservar presupuesto', 'Eliminar presupuesto')
})

test('eliminar una meta de ahorro: botones iguales', async ({ page }) => {
  await irDesdeElMenu(page, 'Metas de Ahorro')
  await page.getByRole('button', { name: 'Nueva Meta' }).click()
  await page.getByLabel('Nombre de la meta').fill('Laptop')
  await page.getByLabel('Monto objetivo (Bs)').fill('1000')
  await page.getByRole('button', { name: 'Crear meta' }).click()
  const tarjeta = page.locator('.meta-card').filter({ hasText: 'Laptop' })
  await tarjeta.getByRole('button', { name: 'Opciones' }).click()
  await page.getByRole('menuitem', { name: 'Eliminar' }).click()
  const dialogo = page.getByRole('dialog', { name: '¿Eliminar meta de ahorro?' })
  await esperarBotonesIguales(dialogo, 'Conservar meta', 'Eliminar meta')
  await expect(tarjeta).toBeVisible()
})

// Patrón 3 (culpa): el límite mensual informa con datos, sin «llevas gastando»
test('el mensaje del límite mensual es neutral y dice cuánto queda', async ({ page }) => {
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Categoría', { exact: true }).selectOption('Comida')
  await page.getByLabel('Monto (Bs)').fill('1000')
  await page.getByRole('button', { name: 'Guardar' }).click()
  const mensaje = page.getByRole('status')
  await expect(mensaje).toContainText('supera tu límite mensual de 500.0 Bs')
  await expect(mensaje).toContainText('Te quedan 460.0 Bs disponibles este mes')
  await expect(mensaje).not.toContainText('llevas gastando')
})
