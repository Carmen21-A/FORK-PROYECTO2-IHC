// Usuarios que crea la semilla (backend/semilla.py) y pasos que comparten las pruebas.
// Martita: limite 500 Bs, presupuesto de Transporte 100 Bs, gasto "Pasaje de micro" 40 Bs
// (pendiente) e ingreso "Mesada" 300 Bs (pagado). Pablo: cuenta nueva, sin datos.
import { expect } from '@playwright/test' // importa la función expect de playwright para realizar aserciones en las pruebas

export const martita = { email: 'martita@presupuesto.com', password: 'martita123' } // datos y credenciales del usuario de prueba martita
export const pablo = { email: 'pablo@presupuesto.com', password: 'pablo123' } // datos y credenciales del usuario de prueba pablo

// Entra desde la pantalla de inicio, como lo haria una persona
export async function iniciarSesion(page, usuario) { // función asíncrona para iniciar sesión con un usuario determinado
  await page.goto('/') // navega a la página principal de la aplicación web
  await page.getByRole('button', { name: 'Iniciar Sesión' }).click() // busca el botón 'Iniciar Sesión' y le hace clic
  await page.getByLabel('Correo electrónico').fill(usuario.email) // escribe el correo electrónico del usuario en el campo correspondiente
  await page.getByLabel('Contraseña', { exact: true }).fill(usuario.password) // escribe la contraseña en el campo de texto exacto
  await page.getByRole('button', { name: 'Iniciar Sesión' }).click() // hace clic en el botón 'Iniciar Sesión' para enviar el formulario
  await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible() // verifica que el título 'Movimientos' sea visible tras iniciar sesión
} // fin de la función iniciarSesion

// Navega con el menu lateral (Movimientos, Historial, Cambiar contraseña...)
export async function irDesdeElMenu(page, opcion) { // función asíncrona para abrir el menú lateral e ir a una sección
  await page.getByRole('button', { name: 'Abrir menú' }).click() // busca el botón 'Abrir menú' y hace clic para desplegarlo
  await page.getByRole('navigation', { name: 'Menú' }).getByRole('button', { name: opcion }).click() // hace clic en el botón de la opción deseada dentro del menú
} // fin de la función irDesdeElMenu

// La fila de un movimiento de la lista, buscada por su descripcion
export function filaDe(page, descripcion) { // función auxiliar que busca un elemento de la lista por su descripción
  return page.getByRole('listitem').filter({ hasText: descripcion }) // retorna el elemento de lista que contenga el texto de la descripción
} // fin de la función filaDe
