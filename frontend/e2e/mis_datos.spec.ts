// Tarea 10 · Mis datos y salida honesta
// Regla de Presupuesto Estudiantil: se elimina todo (movimientos, presupuestos y metas);
// antes puede descargar sus movimientos. Después de eliminarla, la cuenta no puede iniciar sesión.
// La semilla deja a Martita con 2 movimientos (Pasaje de micro y Mesada), 1 límite mensual,
// 1 presupuesto de Transporte y 2 registros en el historial. Pablo es otra cuenta, sin datos.
//
// Evidencia (opcional): FOTOS_TAREA10=1 guarda las capturas en evidencias/tarea-10/
import { readFileSync } from 'node:fs'
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, irDesdeElMenu, martita, pablo } from './usuarios.js'

async function foto(page: Page, nombre: string, fullPage = true) {
  if (process.env.FOTOS_TAREA10) {
    await page.screenshot({ path: `../evidencias/tarea-10/${nombre}.png`, fullPage })
  }
}

// Guarda los eventos que el navegador envía a /api/eventos (para revisar que no lleven datos personales)
function escucharEventos(page: Page) {
  const enviados: { evento: string; props: Record<string, unknown> }[] = []
  page.on('request', (r) => {
    if (r.method() === 'POST' && r.url().endsWith('/api/eventos')) enviados.push(r.postDataJSON())
  })
  return enviados
}

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
  await irDesdeElMenu(page, 'Mis datos')
  await expect(page.getByRole('heading', { name: 'Mis datos' })).toBeVisible()
})

test('Martita ve lo que la app guarda de ella', async ({ page }) => {
  await expect(page.getByText(martita.email)).toBeVisible()
  const resumen = page.getByTestId('resumen-datos')
  await expect(resumen).toContainText('2 movimientos')
  await expect(resumen).toContainText('1 límite mensual')
  await expect(resumen).toContainText('1 presupuesto por categoría')
  await expect(resumen).toContainText('0 metas de ahorro')
  await expect(resumen).toContainText('2 registros del historial')

  const tabla = page.getByRole('table')
  await expect(tabla).toContainText('Pasaje de micro')
  await expect(tabla).toContainText('Mesada')
  await foto(page, '01-mis-datos')
})

test('descarga sus movimientos en CSV y todos sus datos en JSON', async ({ page }) => {
  const enviados = escucharEventos(page)

  const [csv] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: 'Descargar movimientos (CSV)' }).click(),
  ])
  expect(csv.suggestedFilename()).toMatch(/^presupuesto-estudiantil-movimientos-\d{4}-\d{2}-\d{2}\.csv$/)
  const textoCsv = readFileSync(await csv.path(), 'utf-8')
  expect(textoCsv).toContain('Fecha,Tipo,Categoría,Descripción,Monto (Bs),Estado,Se repite')
  expect(textoCsv).toContain('Pasaje de micro')
  expect(textoCsv).toContain('Mesada')
  await expect(page.getByRole('status')).toContainText('Se descargaron tus movimientos (CSV)')
  await foto(page, '02-descarga-csv')

  const [json] = await Promise.all([
    page.waitForEvent('download'),
    page.getByRole('button', { name: 'Descargar todos mis datos (JSON)' }).click(),
  ])
  expect(json.suggestedFilename()).toMatch(/^presupuesto-estudiantil-mis-datos-.*\.json$/)
  const datos = JSON.parse(readFileSync(await json.path(), 'utf-8'))
  expect(datos.cuenta.email).toBe(martita.email)
  expect(datos.movimientos).toHaveLength(2)
  expect(datos.presupuestos_categoria[0]).toMatchObject({ categoria: 'Transporte', monto: 100 })
  expect(JSON.stringify(datos).toLowerCase()).not.toContain('password') // ni la contraseña ni su hash

  // Eventos de la Tarea 9: solo el formato, nunca el contenido descargado
  await expect.poll(() => enviados.map((e) => e.props.formato)).toEqual(['csv', 'json'])
  expect(JSON.stringify(enviados)).not.toContain('Pasaje')
})

test('confirmación honesta: consecuencias reales, botones iguales y conservar no cambia nada', async ({ page }) => {
  const enviados = escucharEventos(page)
  await page.getByRole('button', { name: 'Eliminar mi cuenta' }).click()

  const dialogo = page.getByRole('dialog', { name: '¿Eliminar tu cuenta?' })
  await expect(dialogo).toBeVisible()
  // Consecuencias explicadas con los números reales de Martita
  await expect(dialogo).toContainText('2 movimientos')
  await expect(dialogo).toContainText('1 presupuesto por categoría')
  await expect(dialogo).toContainText('1 límite mensual')
  await expect(dialogo).toContainText(`Ya no podrás iniciar sesión con ${martita.email}`)
  // La regla de la app: antes puede descargar sus movimientos, desde el mismo diálogo
  await expect(dialogo.getByRole('button', { name: 'Descargar mis movimientos (CSV)' })).toBeVisible()
  // Sin pasos de más: no pide escribir «ELIMINAR» ni la contraseña
  await expect(dialogo.getByRole('textbox')).toHaveCount(0)
  await foto(page, '03-confirmacion-honesta', false)

  // Mismo tamaño y estilo: ninguna opción se destaca sobre la otra
  const conservar = dialogo.getByRole('button', { name: 'Conservar mi cuenta' })
  const eliminar = dialogo.getByRole('button', { name: 'Eliminar mi cuenta' })
  expect(await eliminar.getAttribute('class')).toBe(await conservar.getAttribute('class'))
  const [cajaConservar, cajaEliminar] = [await conservar.boundingBox(), await eliminar.boundingBox()]
  expect(Math.abs(cajaConservar!.height - cajaEliminar!.height)).toBeLessThanOrEqual(1)
  // Sin culpa ni presión
  await expect(dialogo).not.toContainText(/te extrañaremos|perderás todo|¿estás segur/i)
  // La salida segura recibe el foco: Enter sin leer no borra la cuenta
  await expect(conservar).toBeFocused()

  // Conservar: un toque, sin «¿seguro?», y todo sigue igual
  await conservar.click()
  await expect(dialogo).toBeHidden()
  await page.reload()
  await expect(page.getByTestId('resumen-datos')).toContainText('2 movimientos')

  await expect
    .poll(() => enviados.map((e) => e.evento))
    .toEqual(['cuenta_eliminacion_iniciada', 'cuenta_eliminacion_frenada'])
  expect(enviados[1].props).toEqual({ motivo: 'conservo_la_cuenta' })
})

test('eliminación completa: la cuenta ya no puede iniciar sesión y las demás no se tocan', async ({ page }) => {
  const enviados = escucharEventos(page)
  const token = await page.evaluate(() => JSON.parse(localStorage.getItem('presupuesto.sesion') ?? '{}').access_token)

  await page.getByRole('button', { name: 'Eliminar mi cuenta' }).click()
  const dialogo = page.getByRole('dialog', { name: '¿Eliminar tu cuenta?' })
  await dialogo.getByRole('button', { name: 'Eliminar mi cuenta' }).click()

  // Vuelve al inicio y se lo dice claro
  await expect(page).toHaveURL(/\/$/)
  await expect(page.getByRole('status')).toContainText('Tu cuenta y todos tus datos se eliminaron')
  await foto(page, '04-cuenta-eliminada')

  // La sesión que tenía abierta ya no sirve
  const conTokenViejo = await page.request.get('/api/movimientos', { headers: { Authorization: `Bearer ${token}` } })
  expect(conTokenViejo.status()).toBe(401)

  // Ya no puede iniciar sesión con esa cuenta
  await page.getByRole('button', { name: 'Iniciar Sesión' }).click()
  await page.getByLabel('Correo electrónico').fill(martita.email)
  await page.getByLabel('Contraseña', { exact: true }).fill(martita.password)
  await page.getByRole('button', { name: 'Iniciar Sesión' }).click()
  await expect(page.getByRole('status')).toContainText('credenciales son incorrectas')
  await expect(page).toHaveURL(/\/login$/)
  await foto(page, '05-login-rechazado')

  // Las otras cuentas siguen funcionando
  await iniciarSesion(page, pablo)

  // Eventos de la Tarea 9: inicio (navegador) y éxito (servidor), sin datos personales
  expect(enviados.map((e) => e.evento)).toEqual(['cuenta_eliminacion_iniciada'])
  expect(JSON.stringify(enviados)).not.toContain(martita.email)
  await irDesdeElMenu(page, 'Analítica')
  const embudo = page.getByTestId('embudo-eliminar_cuenta')
  await expect(embudo).toContainText('Eliminar cuenta (Tarea 10)')
  await expect(embudo).toContainText('100 % terminan')
  await embudo.scrollIntoViewIfNeeded()
  await foto(page, '06-panel-embudo', false)
})
