# Task 04 — Validar el limite mensual de gastos

## Parte 1: Logica de validacion

En `utils/limite_mensual.dart` se agregaron funciones puras:

- `validarMontoLimite`: rechaza texto vacio, letras y montos menores o iguales a 0.
- `esLimiteMenorAGasto`: devuelve `true` si el nuevo limite es menor a lo ya gastado en el mes.
- `superaLimiteMensual`: devuelve `true` si al sumar el nuevo gasto se excede el tope.
- `calcularGastoTotalMes`: suma los gastos validos del mes (excluye ingresos y cancelados).

## Parte 2: Persistencia en Supabase

Se creo `services/limites_service.dart` con dos metodos:

- `getLimit(mes)`: consulta el limite del usuario para ese mes. Retorna `null` si no existe.
- `saveMonthLimit(mes, limite)`: actualiza el registro si ya existe, o lo inserta si es nuevo.

La tabla `limites_mensuales` tiene RLS activado con 4 politicas (SELECT, INSERT, UPDATE, DELETE)
para que cada usuario solo acceda a su propio limite.

## Parte 3: Bloqueo al registrar gastos

En `screens/movements_screen.dart` se agrego la funcion `_validateOverLimit`:

- Si el movimiento es un ingreso, lo deja pasar sin validar.
- Si no hay limite configurado para el mes, lo deja pasar.
- Si al agregar el nuevo gasto se supera el limite, muestra un `SnackBar` rojo y cancela el guardado.
- Si se esta editando, descuenta el monto anterior para no contarlo doble.

El metodo `_save()` delega la verificacion antes de llamar a Supabase:

```dart
final excede = await _validateOverLimit(monto);
if (excede) return;
```

## Parte 4: Interfaz para fijar y visualizar el limite

En `screens/movements_screen.dart` se agregaron dos componentes:

- `_tarjetaResumenLimite`: tarjeta en la parte superior de la pantalla que muestra
  el gasto del mes, el limite fijado y el saldo disponible. Si el disponible llega
  a 0, el texto se pone en rojo. Tiene un boton para definir o cambiar el limite.
- `_dialogoCambiarLimite`: dialogo con un campo numerico validado. Rechaza vacios,
  letras, cero, negativos y limites menores al gasto actual. Al guardar, llama a
  `saveMonthLimit` y refresca la pantalla.

## Parte 5: Pruebas unitarias

Archivo: `test/limite_mensual_test.dart`

| # | Prueba | Que verifica |
|---|--------|----|
| 1 | Montos validos aceptados | `'500'` y `'100.5'` devuelven `null` |
| 2 | Texto vacio o nulo rechazado | `''` y `null` devuelven mensaje de error |
| 3 | Letras rechazadas | `'abc'` y `'abc123'` devuelven mensaje de error |
| 4 | Cero y negativos rechazados | `'0'` y `'-50'` devuelven mensaje de error |
| 5 | Limite menor a gasto rechazado | `esLimiteMenorAGasto(200, 300)` es `true` |
| 6 | Limite mayor a gasto aceptado | `esLimiteMenorAGasto(500, 300)` es `false` |
| 7 | Gasto que excede el limite | `superaLimiteMensual(400, 150, 500)` es `true` |
| 8 | Gasto dentro del limite | `superaLimiteMensual(400, 50, 500)` es `false` |
| 9 | Mensaje de error al exceder | `getMensajesErrorLimiteMensual` retorna texto explicativo |
| 10 | Calculo de gasto mensual | Suma solo gastos validos, excluye cancelados e ingresos |

### Como ejecutar

```bash
flutter test test/limite_mensual_test.dart
```

Resultado esperado:

```
+10: All tests passed!
```
