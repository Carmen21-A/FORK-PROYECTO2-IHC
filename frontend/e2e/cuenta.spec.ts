// Cuenta: registrarse, cambiar la contrasena y recuperarla por correo
import { expect, test } from '@playwright/test'
import { sembrar } from './semilla.js'
import { iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(() => sembrar())

test.describe('Registro', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'Crear una cuenta' }).click()
  })

  test('Lucía crea una cuenta y entra a Movimientos vacío', async ({ page }) => {
    await page.getByLabel('Correo electrónico').fill('lucia@presupuesto.com')
    await page.getByLabel('Contraseña', { exact: true }).fill('lucia123')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible()
    await expect(page.getByText('Aún no tienes movimientos')).toBeVisible()
  })

  test('con un correo ya registrado, le avisa y sigue en el registro', async ({ page }) => {
    await page.getByLabel('Correo electrónico').fill(martita.email)
    await page.getByLabel('Contraseña', { exact: true }).fill('otra1234')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByRole('status')).toContainText('Este correo ya esta registrado')
    await expect(page).toHaveURL(/\/register$/)
  })

  test('con una contraseña corta, le dice el mínimo', async ({ page }) => {
    await page.getByLabel('Correo electrónico').fill('lucia@presupuesto.com')
    await page.getByLabel('Contraseña', { exact: true }).fill('123')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByText('Mínimo 6 caracteres')).toBeVisible()
    await expect(page).toHaveURL(/\/register$/)
  })
})

test.describe('Cambiar contraseña', () => {
  test.beforeEach(async ({ page }) => {
    await iniciarSesion(page, martita)
    await irDesdeElMenu(page, 'Cambiar contraseña')
  })

  test('Martita cambia su contraseña y entra con la nueva', async ({ page }) => {
    await page.getByLabel('Nueva contraseña', { exact: true }).fill('nueva456')
    await page.getByLabel('Repite la nueva contraseña').fill('nueva456')
    await page.getByRole('button', { name: 'Actualizar Contraseña' }).click()

    await expect(page.getByRole('status')).toContainText('Contraseña actualizada')
    await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible()

    // La nueva contrasena funciona al volver a entrar
    await irDesdeElMenu(page, 'Cerrar sesión')
    await iniciarSesion(page, { email: martita.email, password: 'nueva456' })
  })

  test('si las contraseñas no coinciden, le avisa y no cambia nada', async ({ page }) => {
    await page.getByLabel('Nueva contraseña', { exact: true }).fill('nueva456')
    await page.getByLabel('Repite la nueva contraseña').fill('otra7890')
    await page.getByRole('button', { name: 'Actualizar Contraseña' }).click()

    await expect(page.getByText('Las contraseñas no coinciden')).toBeVisible()
    await expect(page).toHaveURL(/\/change-password$/)
  })
})

test.describe('Recuperar contraseña', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.getByRole('button', { name: '¿Olvidaste tu contraseña?' }).click()
  })

  test('Martita pide el enlace y la app le confirma el envío', async ({ page }) => {
    await page.getByLabel('Correo electrónico').fill(martita.email)
    await page.getByRole('button', { name: 'Enviar Solicitud' }).click()

    await expect(page.getByRole('status')).toContainText('recibirás un enlace para cambiar tu contraseña')
    await expect(page).toHaveURL(/\/login$/)
  })

  test('sin correo, le pide que lo escriba', async ({ page }) => {
    await page.getByRole('button', { name: 'Enviar Solicitud' }).click()

    await expect(page.getByText('Ingresa tu correo')).toBeVisible()
    await expect(page).toHaveURL(/\/reset-password$/)
  })
})
