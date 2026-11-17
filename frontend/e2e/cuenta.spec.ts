// Cuenta: registrarse, cambiar la contrasena y recuperarla con un codigo de 4 digitos
import { expect, test } from '@playwright/test'
import { fijarCodigo, sembrar } from './semilla.js'
import { iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(() => sembrar())

test.describe('Registro', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.getByRole('button', { name: 'Crear Cuenta' }).click()
  })

  test('Lucía crea una cuenta y entra a Movimientos vacío', async ({ page }) => {
    await page.getByLabel('Nombre completo').fill('Lucía Pérez')
    await page.getByLabel('Correo electrónico').fill('lucia@presupuesto.com')
    await page.getByLabel('Contraseña', { exact: true }).fill('lucia123')
    await page.getByLabel('Confirmar contraseña').fill('lucia123')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible()
    await expect(page.getByText('Aún no tienes movimientos')).toBeVisible()
  })

  test('sin nombre, le pide que lo escriba y no crea la cuenta', async ({ page }) => {
    await page.getByLabel('Correo electrónico').fill('lucia@presupuesto.com')
    await page.getByLabel('Contraseña', { exact: true }).fill('lucia123')
    await page.getByLabel('Confirmar contraseña').fill('lucia123')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByText('Ingresa tu nombre completo')).toBeVisible()
    await expect(page).toHaveURL(/\/register$/)
  })

  test('con un correo ya registrado, le avisa y sigue en el registro', async ({ page }) => {
    await page.getByLabel('Nombre completo').fill('Otra Martita')
    await page.getByLabel('Correo electrónico').fill(martita.email)
    await page.getByLabel('Contraseña', { exact: true }).fill('otra1234')
    await page.getByLabel('Confirmar contraseña').fill('otra1234')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByRole('status')).toContainText('Este correo ya esta registrado')
    await expect(page).toHaveURL(/\/register$/)
  })

  test('con una contraseña corta, le dice el mínimo', async ({ page }) => {
    await page.getByLabel('Nombre completo').fill('Lucía Pérez')
    await page.getByLabel('Correo electrónico').fill('lucia@presupuesto.com')
    await page.getByLabel('Contraseña', { exact: true }).fill('123')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByText('Mínimo 6 caracteres')).toBeVisible()
    await expect(page).toHaveURL(/\/register$/)
  })

  test('si la confirmación no coincide, le avisa y no crea la cuenta', async ({ page }) => {
    await page.getByLabel('Nombre completo').fill('Lucía Pérez')
    await page.getByLabel('Correo electrónico').fill('lucia@presupuesto.com')
    await page.getByLabel('Contraseña', { exact: true }).fill('lucia123')
    await page.getByLabel('Confirmar contraseña').fill('lucia124')
    await page.getByRole('button', { name: 'Registrarse' }).click()

    await expect(page.getByText('Las contraseñas no coinciden')).toBeVisible()
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

  // Paso 1: Martita escribe su correo y pasa a la pantalla del código
  async function pedirCodigo(page) {
    await page.getByLabel('Correo electrónico').fill(martita.email)
    await page.getByRole('button', { name: 'Enviar código' }).click()
    await expect(page.getByRole('heading', { name: 'Revisa tu correo' })).toBeVisible()
    // El código real llegaría al correo; la prueba lo cambia por uno que conoce
    fijarCodigo(martita.email, '4821')
  }

  test('Martita recibe un código de 4 dígitos, lo escribe y pone su contraseña nueva', async ({ page }) => {
    await pedirCodigo(page)
    await expect(page.getByText('Paso 2 de 3')).toBeVisible()
    await expect(page.getByText(`Si ${martita.email} está registrado, te enviamos un código de 4 dígitos`)).toBeVisible()

    await page.getByLabel('Código de 4 dígitos').fill('4821')
    await page.getByRole('button', { name: 'Verificar código' }).click()

    await expect(page.getByRole('heading', { name: 'Crea tu contraseña nueva' })).toBeVisible()
    await page.getByLabel('Contraseña nueva').fill('martita456')
    await page.getByLabel('Confirmar contraseña').fill('martita456')
    await page.getByRole('button', { name: 'Guardar contraseña' }).click()

    // Entra directo y la contraseña nueva queda guardada
    await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible()
    await expect(page.getByRole('status')).toContainText('tu contraseña se cambió')
    await irDesdeElMenu(page, 'Cerrar sesión')
    await iniciarSesion(page, { ...martita, password: 'martita456' })
  })

  test('con un código equivocado le dice cuántos intentos le quedan y no avanza', async ({ page }) => {
    await pedirCodigo(page)

    await page.getByLabel('Código de 4 dígitos').fill('1111')
    await page.getByRole('button', { name: 'Verificar código' }).click()

    await expect(page.getByText('El código no es correcto. Te quedan 4 intentos.')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Revisa tu correo' })).toBeVisible()
  })

  test('el campo del código solo acepta 4 números', async ({ page }) => {
    await pedirCodigo(page)

    await page.getByLabel('Código de 4 dígitos').pressSequentially('48a2-19')
    await expect(page.getByLabel('Código de 4 dígitos')).toHaveValue('4821')
  })

  test('puede volver a escribir otro correo', async ({ page }) => {
    await pedirCodigo(page)

    await page.getByRole('button', { name: 'Usar otro correo' }).click()
    await expect(page.getByRole('heading', { name: 'Recuperar contraseña' })).toBeVisible()
    await expect(page.getByLabel('Correo electrónico')).toHaveValue(martita.email)
  })

  test('sin correo, le pide que lo escriba', async ({ page }) => {
    await page.getByRole('button', { name: 'Enviar código' }).click()

    await expect(page.getByText('Ingresa tu correo')).toBeVisible()
    await expect(page).toHaveURL(/\/reset-password$/)
  })
})
