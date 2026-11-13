// Clase 22 · Patrones oscuros: el aviso de presupuesto no empuja a pasarse.
// La semilla deja a Martita con presupuesto de Transporte de 100 Bs y un gasto de 40 Bs (Pasaje de micro).
import { expect, test } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, martita } from './usuarios.js'

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
