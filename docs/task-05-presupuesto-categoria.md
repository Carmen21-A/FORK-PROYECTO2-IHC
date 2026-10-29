# Task 05 — Crear presupuesto mensual por categoría y mostrar cuánto se consumió

## Descripción de la tarea

Permite a los estudiantes definir un presupuesto mensual límite para cada una de las categorías de gastos (`Transporte`, `Comida`, `Estudios`, `Ocio`, `Otros`) y visualizar en tiempo real:
1. Cuánto se ha consumido de cada categoría con respecto a su límite asignado.
2. Saldo disponible o exceso por categoría.
3. Indicadores visuales y alertas (verde para consumo normal, ámbar para alerta >= 80%, rojo para presupuesto superado).
4. Desglose detallado de los movimientos que componen el gasto de cada categoría en el mes seleccionado.

---

## Parte 1: Lógica pura de validación y cálculos

Archivo: `lib/utils/presupuesto_categoria.dart`

- `validarMontoPresupuesto(texto)`: valida que el presupuesto ingresado no esté vacío, no contenga letras y sea un número estrictamente mayor a 0.
- `calcularGastoCategoria(movimientos, mes, categoria)`: suma exclusivamente los gastos (`tipo == 'gasto'`) del mes y categoría especificados, excluyendo movimientos cancelados e ingresos.
- `contarMovimientosCategoria(movimientos, mes, categoria)`: cuenta la cantidad de movimientos válidos registrados.
- `calcularPorcentajeConsumo(presupuestado, consumido)`: calcula el porcentaje consumido (`consumido / presupuestado`).
- `calcularSaldoRestante(presupuestado, consumido)`: calcula la diferencia (`presupuestado - consumido`), indicando disponibilidad o exceso.
- `obtenerEstadoPresupuesto(presupuestado, consumido)`: determina el estado:
  - `sinPresupuesto`: cuando no se ha definido límite.
  - `optimo`: consumo menor al 80%.
  - `alerta`: consumo entre 80% y 100%.
  - `excedido`: consumo supera el 100%.
- `construirResumenMensual(...)`: consolida las 5 categorías, calcula métricas globales (Total Presupuestado, Total Consumido, Total Restante) y detecta listas de categorías en alerta y excedidas.

---

## Parte 2: Persistencia en Supabase

Archivos:
- `lib/services/presupuestos_service.dart`
- `supabase/presupuestos_categoria.sql`

El servicio ofrece persistencia robusta con soporte dual:
1. Si la tabla `presupuestos_categoria` está creada en Supabase, interactúa directamente con ella mediante políticas RLS por `user_id`.
2. Como fallback resiliente e inmediato, almacena las claves en `limites_mensuales` con el formato `${mes}#${categoria}`, garantizando que la funcionalidad opere sin interrupciones con la base de datos actual del proyecto.

Métodos disponibles:
- `getPresupuestosMes(mes)`: consulta todos los presupuestos del mes para el usuario autenticado.
- `savePresupuestoCategoria(mes, categoria, monto)`: inserta o actualiza el presupuesto de la categoría.
- `deletePresupuestoCategoria(mes, categoria)`: elimina el presupuesto asignado a la categoría.
- `getResumenMensual(mes, movimientos)`: genera el resumen integral de consumo vs presupuesto.

---

## Parte 3: Interfaz de usuario (UI/UX)

Archivo: `lib/screens/presupuesto_categoria_screen.dart`

Cumple con el sistema de diseño (`ColorStyles`, `AppTextStyle`, `SpacingTokens`):

1. **Selector de mes:** Navegación mes a mes con botones anterior/siguiente y display del mes actual (`Mes Año`).
2. **Tarjeta de Resumen Ejecutivo:**
   - Métricas: Total Presupuestado, Total Consumido y Saldo Restante / Exceso.
   - Barra de progreso general con degradado y porcentaje global.
3. **Banner de Alertas:**
   - Informa de manera inmediata si alguna categoría ha superado su presupuesto o está cerca de alcanzarlo (>= 80%).
4. **Tarjetas por Categoría:**
   - Icono y color temático por cada categoría universitaria.
   - Badge de estado con icono descriptivo.
   - Barra de progreso porcentual coloreada dinámicamente (verde/ámbar/rojo).
   - Datos clave: Presupuestado, Consumido (con conteo de gastos) y Disponible/Exceso.
   - Acciones para definir, editar o eliminar presupuesto con diálogo modal validado y accesos rápidos (`+50 Bs`, `+100 Bs`, etc.).
   - Sección desplegable para ver el detalle de los gastos individuales de la categoría en ese mes.

---

## Parte 4: Integración en navegación

- `lib/router/app_router.dart`: Ruta privada `/presupuestos-categoria` protegida por autenticación de Supabase.
- `lib/widgets/app_drawer.dart`: Opción en el menú lateral "Presupuesto por Categoría" con icono `pie_chart`.
- `lib/screens/movements_screen.dart`: Botón de acceso directo en la tarjeta de límite mensual para navegar con un clic.

---

## Parte 5: Pruebas unitarias automatizadas

Archivo: `test/presupuesto_categoria_test.dart`

| # | Prueba | Verificación |
|---|--------|--------------|
| 1 | Montos válidos aceptados | `'350'`, `'150.50'` devuelven `null` |
| 2 | Texto vacío rechazado | `''`, `'   '` y `null` retornan error |
| 3 | Letras rechazadas | `'abc'`, `'100Bs'` retornan error |
| 4 | Cero y negativos rechazados | `'0'`, `'-20'` retornan error |
| 5 | Cálculo de consumo por categoría | Suma únicamente gastos del mes y categoría |
| 6 | Cálculo por categoría específica | Comprueba aislamiento de Transporte frente a Comida |
| 7 | Categoría sin gastos | Devuelve `0.0` |
| 8 | Conteo de movimientos | Cuenta transacciones válidas |
| 9 | Porcentaje de consumo | `consumido / presupuestado` |
| 10 | Saldo restante positivo y exceso | Saldo restante positivo y negativo |
| 11 | Estado sin presupuesto | Cuando no hay límite configurado |
| 12 | Estado óptimo | Consumo < 80% |
| 13 | Estado de alerta | Consumo entre 80% y 100% |
| 14 | Estado excedido | Consumo > 100% |
| 15 | Resumen mensual completo | Totales generales y detección de alertas/excesos |

### Ejecución de pruebas

```bash
flutter test test/presupuesto_categoria_test.dart
```

Resultado:
```
00:00 +15: All tests passed!
```
