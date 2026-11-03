// Diseno: consistencia visual (H4), accesibilidad (axe) y tamano de los botones (Fitts)
import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(() => sembrar())

// Revisa la pagina con axe y devuelve cada problema en una linea: "regla: elemento"
async function problemasDeAccesibilidad(page: Page) {
  // Sin la fuente de iconos cargada, axe lee "more_vert" como texto del boton
  await page.evaluate(() => document.fonts.ready)
  const { violations } = await new AxeBuilder({ page }).analyze()
  return violations.flatMap((v) => v.nodes.map((n) => `${v.id}: ${n.target.join(' ')}`))
}

// ---------- Regresion visual: pantallas que no dependen de la fecha ni de los datos ----------
const pantallasFijas = [
  { nombre: 'inicio', ruta: '/' },
  { nombre: 'login', ruta: '/login' },
  { nombre: 'registro', ruta: '/register' },
  { nombre: 'recuperar', ruta: '/reset-password' },
]

for (const { nombre, ruta } of pantallasFijas) {
  test(`la pantalla de ${nombre} se ve igual que la captura base`, async ({ page }) => {
    await page.goto(ruta)
    await page.evaluate(() => document.fonts.ready)

    await expect(page).toHaveScreenshot(`${nombre}.png`)
  })
}

// ---------- Accesibilidad: cada pantalla de la app, sin problemas segun axe ----------
const pantallas: { nombre: string; abrir: (page: Page) => Promise<void> }[] = [
  ...pantallasFijas.map(({ nombre, ruta }) => ({
    nombre,
    abrir: async (page: Page) => {
      await page.goto(ruta)
    },
  })),
  {
    nombre: 'Movimientos',
    abrir: async (page) => {
      await iniciarSesion(page, martita)
      await expect(page.getByText('Pasaje de micro')).toBeVisible()
    },
  },
  {
    nombre: 'formulario de nuevo movimiento',
    abrir: async (page) => {
      await iniciarSesion(page, martita)
      await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
      await expect(page.getByRole('dialog', { name: 'Nuevo gasto o ingreso' })).toBeVisible()
    },
  },
  {
    nombre: 'límite mensual',
    abrir: async (page) => {
      await iniciarSesion(page, martita)
      await page.getByRole('button', { name: 'Cambiar', exact: true }).click()
      await expect(page.getByRole('dialog', { name: 'Límite mensual de gastos' })).toBeVisible()
    },
  },
  {
    nombre: 'Presupuesto por Categoría',
    abrir: async (page) => {
      await iniciarSesion(page, martita)
      await page.getByRole('button', { name: 'Presupuestos por Categoría' }).click()
      await expect(page.getByRole('article').first()).toBeVisible()
    },
  },
  {
    nombre: 'Historial',
    abrir: async (page) => {
      await iniciarSesion(page, martita)
      await irDesdeElMenu(page, 'Historial')
      await expect(page.getByText('Pasaje de micro')).toBeVisible()
    },
  },
  {
    nombre: 'Cambiar contraseña',
    abrir: async (page) => {
      await iniciarSesion(page, martita)
      await irDesdeElMenu(page, 'Cambiar contraseña')
      await expect(page.getByRole('button', { name: 'Actualizar Contraseña' })).toBeVisible()
    },
  },
]

for (const { nombre, abrir } of pantallas) {
  test(`${nombre} no tiene problemas de accesibilidad`, async ({ page }) => {
    await abrir(page)

    expect(await problemasDeAccesibilidad(page)).toEqual([])
  })
}

// ---------- Fitts: los botones del flujo principal miden al menos 44 px ----------
test('los botones del flujo son fáciles de tocar (Fitts)', async ({ page }) => {
  await iniciarSesion(page, martita)
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()

  for (const nombre of ['Abrir menú', 'Nuevo Movimiento', 'Guardar']) {
    const caja = await page.getByRole('button', { name: nombre }).boundingBox()
    expect(caja!.width, `ancho de "${nombre}"`).toBeGreaterThanOrEqual(44)
    expect(caja!.height, `alto de "${nombre}"`).toBeGreaterThanOrEqual(44)
  }
})
