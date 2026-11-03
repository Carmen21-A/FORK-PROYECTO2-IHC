// Clase 18 - Reto: "Presupuesto: Registrar gasto -> el total cambia"
// Semilla -> Login -> Crear -> Lo ve en pantalla
// La semilla (backend/semilla.py) deja a Martita con un limite de 500 Bs y un gasto de 40 Bs.
import { expect, test, type Page } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, martita, pablo } from './usuarios.js'

// Estas pruebas cambian datos: cada una empieza desde la semilla
test.beforeEach(() => sembrar())

async function llenarLogin(page: Page, email: string, password: string) {
  await page.goto('/login')
  await page.getByLabel('Correo electrónico').fill(email)
  await page.getByLabel('Contraseña', { exact: true }).fill(password)
  await page.getByRole('button', { name: 'Iniciar Sesión' }).click()
}

async function llenarGasto(page: Page, monto: string, descripcion = '') {
  await page.getByRole('button', { name: 'Nuevo Movimiento' }).click()
  await page.getByLabel('Categoría', { exact: true }).selectOption('Comida')
  await page.getByLabel('Monto (Bs)').fill(monto)
  await page.getByLabel('Descripción (opcional)').fill(descripcion)
}

// ============================================================================
// CAMINO FELIZ: el usuario hace todo bien
// ============================================================================
test.describe('Camino feliz', () => {
  test('Martita registra un gasto y el total cambia', async ({ page }) => {
    // 1. Login (desde la pantalla de inicio, como una persona)
    await iniciarSesion(page, martita)
    await expect(page.getByText('Total gastos: 40.0 Bs')).toBeVisible()

    // 2. Crear: un gasto de 25.5 Bs
    await llenarGasto(page, '25.5', 'Almuerzo')
    await page.getByRole('button', { name: 'Guardar' }).click()

    // 3. Lo ve en pantalla. Exito: mensaje y dato nuevo
    await expect(page.getByRole('status')).toContainText('Gasto registrado')
    await expect(page.getByText('Total gastos: 65.5 Bs')).toBeVisible()
    await expect(page.getByText('Gastado: 65.5 Bs')).toBeVisible()
    await expect(page.getByRole('listitem').filter({ hasText: 'Almuerzo' })).toContainText('- 25.5 Bs')

    // 4. Persistencia: sigue al recargar
    await page.reload()
    await expect(page.getByText('Total gastos: 65.5 Bs')).toBeVisible()
  })

  test('Pablo no ve los gastos de Martita y sabe cómo registrar el primero', async ({ page }) => {
    await iniciarSesion(page, pablo)

    // Vacio: mensaje y accion
    await expect(page.getByText('Aún no tienes movimientos')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Nuevo Movimiento' })).toBeVisible()
    await expect(page.getByText('Pasaje de micro')).toHaveCount(0)
    await expect(page.getByText('Total gastos: 0.0 Bs')).toBeVisible()
  })
})

// ============================================================================
// CAMINO ALTERNATIVO: el usuario se equivoca al iniciar sesion
// Error: le dice que corregir y no lo deja entrar
// ============================================================================
test.describe('Camino alternativo: inicio de sesión', () => {
  test('con una contraseña incorrecta, ve el error y sigue en el login', async ({ page }) => {
    await llenarLogin(page, martita.email, 'incorrecta')

    await expect(page.getByRole('status')).toContainText('Las credenciales son incorrectas')
    await expect(page).toHaveURL(/\/login$/)
  })

  test('con un correo que no está registrado, ve el error y sigue en el login', async ({ page }) => {
    await llenarLogin(page, 'noexiste@presupuesto.com', martita.password)

    await expect(page.getByRole('status')).toContainText('Las credenciales son incorrectas')
    await expect(page).toHaveURL(/\/login$/)
  })

  test('con un correo mal escrito, le pide un correo válido', async ({ page }) => {
    await llenarLogin(page, 'martita.presupuesto.com', martita.password)

    await expect(page.getByRole('status')).toContainText('Ingresa un correo válido')
    await expect(page).toHaveURL(/\/login$/)
  })

  test('con los campos vacíos, le dice qué llenar', async ({ page }) => {
    await llenarLogin(page, '', '')

    await expect(page.getByText('Ingresa tu correo')).toBeVisible()
    await expect(page.getByText('Mínimo 6 caracteres')).toBeVisible()
    await expect(page).toHaveURL(/\/login$/)
  })
})

// ============================================================================
// CAMINO ALTERNATIVO: el usuario se equivoca al registrar el gasto
// El gasto no se guarda y el total NO cambia
// ============================================================================
test.describe('Camino alternativo: registrar gasto', () => {
  test.beforeEach(async ({ page }) => {
    await iniciarSesion(page, martita)
  })

  test('si el gasto supera el límite, se bloquea y el total no cambia', async ({ page }) => {
    await llenarGasto(page, '1000', 'Celular')
    // Aviso en vivo antes de guardar
    await expect(page.getByText(/Supera tu límite mensual/)).toBeVisible()
    await page.getByRole('button', { name: 'Guardar' }).click()

    await expect(page.getByRole('status')).toContainText('No se puede registrar, porque supera tu límite')
    await page.keyboard.press('Escape')
    await expect(page.getByText('Total gastos: 40.0 Bs')).toBeVisible()
    await expect(page.getByText('Celular')).toHaveCount(0)
  })

  test('sin monto, le dice qué corregir y no guarda', async ({ page }) => {
    await llenarGasto(page, '')
    await page.getByRole('button', { name: 'Guardar' }).click()

    await expect(page.getByText('El campo no puede estar vacío')).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(page.getByText('Total gastos: 40.0 Bs')).toBeVisible()
  })

  test('con letras en el monto, le dice qué corregir y no guarda', async ({ page }) => {
    await llenarGasto(page, 'veinte')
    await page.getByRole('button', { name: 'Guardar' }).click()

    await expect(page.getByText('Formato numérico inválido')).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(page.getByText('Total gastos: 40.0 Bs')).toBeVisible()
  })
})
