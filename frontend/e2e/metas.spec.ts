// Pruebas E2E: Metas de Ahorro con Fondos Disponibles (Tarea 8)
import { expect, test } from '@playwright/test'
import { sembrar } from './semilla.js'
import { filaDe, iniciarSesion, irDesdeElMenu, martita } from './usuarios.js'

test.beforeEach(async ({ page }) => {
  sembrar()
  await iniciarSesion(page, martita)
})

test.describe('Metas de Ahorro y Fondos Disponibles', () => {
  test('Recorrido completo: crear 2 metas, asignar fondos, transferir, retirar y conservar saldo total', async ({
    page,
  }) => {
    // 1. Navegar a Metas de Ahorro desde el menú lateral
    await irDesdeElMenu(page, 'Metas de Ahorro')
    await expect(page.getByRole('heading', { name: 'Metas de Ahorro', exact: true })).toBeVisible()

    // 2. Comprobar saldos iniciales de Martita (Ingreso 300 Bs pagado, Gasto 0 Bs pagado)
    await expect(page.getByText('Saldo Total', { exact: true })).toBeVisible()
    await expect(page.getByText('300.0 Bs').first()).toBeVisible()
    await expect(page.getByText('Saldo Disponible', { exact: true })).toBeVisible()

    // 3. Crear Meta 1: "Laptop de estudio" (Objetivo: 1000 Bs)
    await page.getByRole('button', { name: 'Nueva Meta' }).click()
    await page.getByLabel('Nombre de la meta').fill('Laptop de estudio')
    await page.getByLabel('Monto objetivo (Bs)').fill('1000')
    await page.getByRole('button', { name: 'Crear meta' }).click()

    await expect(page.getByText('Laptop de estudio')).toBeVisible()
    await expect(page.getByText('0.0 Bs ahorrados de 1000.0 Bs')).toBeVisible()

    // 4. Crear Meta 2: "Viaje de graduación" (Objetivo: 500 Bs)
    await page.getByRole('button', { name: 'Nueva Meta' }).click()
    await page.getByLabel('Nombre de la meta').fill('Viaje de graduación')
    await page.getByLabel('Monto objetivo (Bs)').fill('500')
    await page.getByRole('button', { name: 'Crear meta' }).click()

    await expect(page.getByText('Viaje de graduación')).toBeVisible()

    // 5. Asignar 100 Bs del saldo disponible a Meta 1 ("Laptop de estudio")
    const tarjetaLaptop = page.locator('.meta-card').filter({ hasText: 'Laptop de estudio' })
    await tarjetaLaptop.getByRole('button', { name: 'Asignar fondos' }).click()

    await expect(page.locator('.info-operacion')).toContainText('300.0 Bs')
    await page.getByLabel(/Monto a asignar/i).fill('100')
    await page.getByRole('button', { name: 'Confirmar asignación' }).click()

    // Verificar consecuencias en pantalla:
    // Meta 1 tiene 100 Bs ahorrados (10%)
    await expect(tarjetaLaptop.getByText('100.0 Bs ahorrados de 1000.0 Bs')).toBeVisible()
    await expect(tarjetaLaptop.getByText('10%')).toBeVisible()

    // Fondos reservados en metas sube a 100 Bs, Saldo disponible baja a 200 Bs, Saldo total se conserva en 300 Bs
    await expect(page.getByText('100.0 Bs').first()).toBeVisible()
    await expect(page.getByText('200.0 Bs')).toBeVisible()
    await expect(page.getByText('300.0 Bs')).toBeVisible()

    // 6. Transferir 40 Bs de Meta 1 ("Laptop") a Meta 2 ("Viaje")
    await tarjetaLaptop.getByRole('button', { name: 'Transferir' }).click()
    await page.getByLabel('Meta de destino').selectOption({ label: 'Viaje de graduación' })
    await page.getByLabel(/Monto a transferir/i).fill('40')
    await page.getByRole('button', { name: 'Confirmar transferencia' }).click()

    // Meta 1 baja a 60 Bs
    await expect(tarjetaLaptop.getByText('60.0 Bs ahorrados de 1000.0 Bs')).toBeVisible()

    // Meta 2 sube a 40 Bs
    const tarjetaViaje = page.locator('.meta-card').filter({ hasText: 'Viaje de graduación' })
    await expect(tarjetaViaje.getByText('40.0 Bs ahorrados de 500.0 Bs')).toBeVisible()

    // El saldo total y disponible se conservan
    await expect(page.getByText('200.0 Bs')).toBeVisible()
    await expect(page.getByText('300.0 Bs')).toBeVisible()

    // 7. Retirar 15 Bs de Meta 2 ("Viaje") hacia el saldo disponible
    await tarjetaViaje.getByRole('button', { name: 'Retirar' }).click()
    await page.getByLabel(/Monto a retirar/i).fill('15')
    await page.getByRole('button', { name: 'Confirmar retiro' }).click()

    // Meta 2 queda en 25 Bs
    await expect(tarjetaViaje.getByText('25.0 Bs ahorrados de 500.0 Bs')).toBeVisible()

    // Saldo disponible sube a 215 Bs (200 + 15)
    await expect(page.getByText('215.0 Bs')).toBeVisible()
    await expect(page.getByText('300.0 Bs')).toBeVisible()

    // 8. Persistencia: Recargar la página y verificar que los datos se conservan
    await page.reload()
    await expect(page.getByText('Laptop de estudio')).toBeVisible()
    await expect(page.getByText('Viaje de graduación')).toBeVisible()
    await expect(page.getByText('215.0 Bs')).toBeVisible()
    await expect(page.getByText('300.0 Bs')).toBeVisible()

    // 9. Conservar movimientos: Las metas NO deben generar movimientos de gastos ficticios
    await irDesdeElMenu(page, 'Movimientos')
    await expect(page.getByRole('heading', { name: 'Movimientos' })).toBeVisible()
    // Solo deben existir los 2 movimientos de la semilla ("Pasaje de micro" y "Mesada")
    await expect(page.locator('.list-tile')).toHaveCount(2)
  })

  test('Restricción importante: Rechazar operaciones sin fondos disponibles o fondos insuficientes', async ({
    page,
  }) => {
    await irDesdeElMenu(page, 'Metas de Ahorro')

    // Crear meta
    await page.getByRole('button', { name: 'Nueva Meta' }).click()
    await page.getByLabel('Nombre de la meta').fill('Fondo de emergencia')
    await page.getByLabel('Monto objetivo (Bs)').fill('500')
    await page.getByRole('button', { name: 'Crear meta' }).click()

    const tarjeta = page.locator('.meta-card').filter({ hasText: 'Fondo de emergencia' })
    await tarjeta.getByRole('button', { name: 'Asignar fondos' }).click()

    // Saldo disponible de Martita es 300 Bs. Intenta asignar 450 Bs
    await page.getByLabel(/Monto a asignar/i).fill('450')

    // Se detecta y bloquea la operación informando claramente
    await expect(page.getByText(/Fondos insuficientes: el saldo disponible es de 300.0 Bs/)).toBeVisible()
    await expect(page.getByRole('button', { name: 'Confirmar asignación' })).toBeDisabled()

    // Si cancela, la meta sigue en 0 Bs
    await page.getByRole('button', { name: 'Cancelar' }).click()
    await expect(tarjeta.getByText('0.0 Bs ahorrados de 500.0 Bs')).toBeVisible()

    // Asignar monto válido de 50 Bs
    await tarjeta.getByRole('button', { name: 'Asignar fondos' }).click()
    await page.getByLabel(/Monto a asignar/i).fill('50')
    await page.getByRole('button', { name: 'Confirmar asignación' }).click()
    await expect(tarjeta.getByText('50.0 Bs ahorrados de 500.0 Bs')).toBeVisible()

    // Intentar retirar 120 Bs cuando la meta solo tiene 50 Bs
    await tarjeta.getByRole('button', { name: 'Retirar' }).click()
    await page.getByLabel(/Monto a retirar/i).fill('120')

    await expect(page.getByText(/Fondos insuficientes en la meta: cuenta con 50.0 Bs/)).toBeVisible()
    await expect(page.getByRole('button', { name: 'Confirmar retiro' })).toBeDisabled()
  })

  test('Restricción: el dinero reservado en metas no se puede gastar al pagar un gasto', async ({ page }) => {
    // Martita tiene 300 Bs. Reserva 280 Bs en una meta: le quedan 20 Bs disponibles
    await irDesdeElMenu(page, 'Metas de Ahorro')
    await page.getByRole('button', { name: 'Nueva Meta' }).click()
    await page.getByLabel('Nombre de la meta').fill('Matrícula')
    await page.getByLabel('Monto objetivo (Bs)').fill('500')
    await page.getByRole('button', { name: 'Crear meta' }).click()

    const tarjeta = page.locator('.meta-card').filter({ hasText: 'Matrícula' })
    await tarjeta.getByRole('button', { name: 'Asignar fondos' }).click()
    await page.getByLabel(/Monto a asignar/i).fill('280')
    await page.getByRole('button', { name: 'Confirmar asignación' }).click()
    await expect(tarjeta.getByText('280.0 Bs ahorrados de 500.0 Bs')).toBeVisible()

    // Intenta pagar el "Pasaje de micro" de 40 Bs: solo tiene 20 Bs libres
    await irDesdeElMenu(page, 'Movimientos')
    await filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pendiente' }).click()

    // Se rechaza explicando el motivo y el gasto sigue pendiente
    await expect(page.getByText(/Fondos insuficientes: tienes 280.00 Bs reservados en tus metas/)).toBeVisible()
    await expect(filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pendiente' })).toBeVisible()

    // Persistencia: tras recargar, el gasto sigue pendiente y la meta conserva sus 280 Bs
    await page.reload()
    await expect(filaDe(page, 'Pasaje de micro').getByRole('button', { name: 'pendiente' })).toBeVisible()
    await irDesdeElMenu(page, 'Metas de Ahorro')
    await expect(tarjeta.getByText('280.0 Bs ahorrados de 500.0 Bs')).toBeVisible()
    await expect(page.getByText('20.0 Bs').first()).toBeVisible()
  })
})
