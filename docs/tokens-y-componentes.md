# Tokens y componentes: Figma ↔ código

## 1. Regla

- **Todos los valores** (colores, espacios, tamaños de texto, sombras, radios) se escriben **una sola vez**, en el bloque `:root` de [`frontend/src/design_system/tokens.css`](../frontend/src/design_system/tokens.css).
- El resto del CSS **solo llama al token**: `background: var(--color-accion);`. Nunca `#0f766e` suelto ni `var(--color-accion, #0f766e)` con un color de respaldo.
- Los nombres dicen **para qué sirve** el valor (`accion`, `error`, `fondo`, `espacio-4`), no qué color es.
- **El mismo nombre en Figma:** el token CSS `--color-accion` es la variable `color/accion` en Figma (colección «Tokens»). Se cambia el primer `-` por `/`.
- **Comprobado por una prueba:** [`frontend/tests/unit/tokens.test.js`](../frontend/tests/unit/tokens.test.js) falla si aparece un color escrito a mano fuera de `tokens.css`, si se usa un token que no existe o si un token tiene un nombre que no sigue la regla.

```css
:root {
  --color-accion: #0f766e;
  --color-error: #b91c1c;
  --espacio-2: 8px;
  --espacio-4: 16px;
}

.btn-elevated {
  background: var(--color-accion);
  padding: var(--espacio-2) var(--espacio-4);
}
```

## 2. Tokens principales

| Token CSS | Variable en Figma | Valor | Para qué se usa |
|---|---|---|---|
| `--color-accion` | `color/accion` | `#0f766e` | Botones principales, pestaña activa, foco, «Nuevo Movimiento» |
| `--color-accion-hover` | `color/accion-hover` | `#115e59` | Botón al pasar el mouse; texto de los botones de contorno |
| `--color-accion-claro` | `color/accion-claro` | `#ccfbf1` | Filtro elegido, fondo suave de acción |
| `--color-texto-sobre-accion-claro` | `color/texto-sobre-accion-claro` | `#042f2e` | Texto sobre `--color-accion-claro` |
| `--color-barra` | `color/barra` | `#262058` | Barra superior y cabecera del menú |
| `--color-barra-fin` | `color/barra-fin` | `#3a3184` | Final del degradado de la barra |
| `--color-fondo` | `color/fondo` | `#f7f8fb` | Fondo de las pantallas |
| `--color-superficie` | `color/superficie` | `#ffffff` | Tarjetas, diálogos y campos |
| `--color-borde` | `color/borde` | `#667085` | Borde de los campos |
| `--color-texto` | `color/texto` | `#1f2937` | Texto normal |
| `--color-texto-secundario` | `color/texto-secundario` | `#6b7280` | Fechas y ayudas |
| `--color-texto-inverso` | `color/texto-inverso` | `#ffffff` | Texto sobre botones y barra |
| `--color-error` | `color/error` | `#b91c1c` | Mensajes de error, gastos, eliminar |
| `--color-exito` | `color/exito` | `#15803d` | Ingresos, «en orden» |
| `--color-advertencia` | `color/advertencia` | `#b45309` | Avisos: 80 % del límite, aviso de presupuesto |
| `--color-pendiente` | `color/pendiente` | `#1565c0` | Estado «pendiente» y contador «Por pagar» |
| `--color-pagado` | `color/pagado` | `#2e7d32` | Estado «pagado» |
| `--color-categoria-fondo` | `color/categoria-fondo` | `#f1f5f9` | Etiqueta de categoría |
| `--color-publico-accion` | `color/publico-accion` | `#1d4ed8` | Botones de Inicio, login, registro y recuperar |
| `--color-publico-titulo` | `color/publico-titulo` | `#1b2440` | Títulos de las páginas públicas |
| `--espacio-1` · `--espacio-2` · `--espacio-4` · `--espacio-6` · `--espacio-8` · `--espacio-12` | `espacio/1` … `espacio/12` | 4 · 8 · 16 · 24 · 32 · 48 px | Márgenes y separaciones |
| `--texto-micro` … `--texto-titulo` | `texto/micro` … `texto/titulo` | 12 · 14 · 16 · 18 · 20 · 24 · 30 px | Tamaños de letra (lámina «Tipografía») |
| `--fuente` | `fuente` | Inter | Toda la app |

La lista completa (unos 100 tokens, con estados, categorías, grises, velos y sombras) está en `tokens.css`, agrupada y comentada.

## 3. Tabla componente ↔ archivo

| Componente en Figma | Clase CSS | Archivo de estilos | Dónde se usa (pantallas) |
|---|---|---|---|
| `Botón/Primario` | `.pub-btn.pub-btn-primario` | `theme/paginasPublicas.css` | `HomeScreen.vue`, `LoginScreen.vue`, `RegisterScreen.vue`, `ResetPasswordScreen.vue`, `widgets/BarraPublica.vue` |
| `Botón/Secundario` | `.pub-btn.pub-btn-secundario` | `theme/paginasPublicas.css` | `HomeScreen.vue` («Ver Cómo Funciona») |
| `Botón/Texto barra` | `.pub-btn.pub-btn-texto` | `theme/paginasPublicas.css` | `widgets/BarraPublica.vue` («Iniciar Sesión») |
| `Botón/Enlace` | `.auth-enlace` | `theme/paginasPublicas.css` | `LoginScreen.vue`, `RegisterScreen.vue`, `ResetPasswordScreen.vue` |
| `Botón/Acción destacada` | `.btn.btn-elevated` | `theme/appTheme.css` | `MovementsScreen.vue` («Buscar», «Guardar»), `MetasScreen.vue`, diálogos |
| `Botón/Contorno` | `.btn.btn-outlined` | `theme/appTheme.css` | «Cambiar», «Más filtros», «Ayuda», confirmaciones en `MovementsScreen.vue`, `MetasScreen.vue`, `MisDatosScreen.vue` |
| `Botón/FAB` | `.fab` | `theme/appTheme.css` | `MovementsScreen.vue` («Nuevo Movimiento») |
| `Botón/Pestaña` | `.tabs-arquitectura .tab-item` | `theme/appTheme.css` | `MovementsScreen.vue`, `MetasScreen.vue` |
| `Botón/Menú lateral` | `.drawer-item` | `theme/appTheme.css` | `widgets/AppDrawer.vue` |
| `Campo/Público`, `Campo/Registro ancho` | `.field` + `.input` (dentro de `.auth-formulario`) | `theme/paginasPublicas.css` + `theme/appTheme.css` | `LoginScreen.vue`, `RegisterScreen.vue`, `ResetPasswordScreen.vue` |
| `Campo/Contraseña`, `Campo/Registro contraseña` | `widgets/PasswordField.vue` (`.input.has-suffix`) | `theme/appTheme.css` | `LoginScreen.vue`, `RegisterScreen.vue`, `ResetPasswordScreen.vue`, `ChangePasswordScreen.vue` |
| `Campo/App`, `Campo/App ancho` | `.field` + `.input` | `theme/appTheme.css` | `MovementsScreen.vue` (monto, descripción), `MetasScreen.vue`, `PresupuestoCategoriaScreen.vue` |
| `Campo/App contraseña` | `widgets/PasswordField.vue` | `theme/appTheme.css` | `ChangePasswordScreen.vue` |
| Barra superior (`Base/…`) | `.app-bar.primary` | `theme/appTheme.css` | `widgets/AppScaffold.vue` (todas las pantallas con sesión) |
| `Menú lateral` | `.drawer`, `.drawer-header` | `theme/appTheme.css` | `widgets/AppDrawer.vue` |
| `Diálogo/…` | `.overlay`, `.dialog` | `theme/appTheme.css` | `widgets/AppDialog.vue` |
| `Hoja/Nuevo movimiento` | `.sheet` | `theme/appTheme.css` | `MovementsScreen.vue` |
| `Logo` | `.marca` | `widgets/MarcaLogo.vue` | `widgets/BarraPublica.vue` |
