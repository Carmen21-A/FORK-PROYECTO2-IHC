# Task 04 — Busqueda y filtros de movimientos

## Parte 1: Interfaz de busqueda y filtros

En `screens/movements_screen.dart` se agrego:

- Un campo de busqueda por **descripcion** (coincidencia parcial).
- Selectores de filtro por **tipo**, **categoria**, **periodo** (este mes, mes pasado o un rango de fechas) y **estado**.
- Los filtros activos se muestran como `Chip` con opcion de quitarlos.
- Si ningun movimiento coincide, se muestra el mensaje:
  > "No hay movimientos que coincidan con la busqueda"

Los filtros se pueden combinar (por ejemplo: gastos de comida de este mes).

## Parte 2: Consulta en services

En `services/movements_service.dart` se agrego el metodo `buscarConFiltros`,
que combina la busqueda y los filtros en una sola consulta a Supabase:

- Descripcion con `ilike` (coincidencia parcial).
- `eq` para tipo, categoria y estado.
- `gte` / `lte` para el rango de fechas.

Cada filtro es opcional, asi que se pueden combinar varios a la vez. El flujo
queda: interfaz → consulta → base de datos.

## Parte 3: Total de movimientos filtrados

En `utils/movimientos_filtros.dart`:

- `calcularMontoTotalMovimientos` suma los montos de la lista.
- El total se muestra en pantalla y usa la misma lista que el `ListView`, por
  lo que siempre coincide con lo que se ve.

La funcion `filtrarMovimientos` del mismo archivo concentra la logica de
filtrado (version pura, para las pruebas).

## Parte 4: Pruebas unitarias

Archivo: `test/movimientos_filtros_test.dart`

| # | Prueba | Que verifica |
|---|--------|--------------|
| 1 | Caso con resultados | Filtra por descripcion parcial y por tipo |
| 2 | Caso sin resultados | Devuelve lista vacia cuando nada coincide |
| 3 | Combinacion de filtros | Combina tipo+categoria+estado y texto+tipo+fechas |
| 4 | Total | El total es la suma de los movimientos filtrados |

### Como ejecutar

```bash
flutter test test/movimientos_filtros_test.dart
```

Resultado esperado:

```
+6: All tests passed!
```
