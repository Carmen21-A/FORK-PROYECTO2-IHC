# Frontend: Vue 3

Interfaz web de Presupuesto Estudiantil. Es la misma app que había en Flutter, pantalla por pantalla.

## Estructura (equivalencia con `lib/` de Flutter)

```
frontend/src/
├── main.js                 # lib/main.dart
├── env.js                  # lib/env.dart
├── router/appRouter.js     # lib/router/app_router.dart (rutas privadas)
├── design_system/          # lib/design_system (colores, espaciados, textos)
├── theme/                  # lib/theme/app_theme.dart
├── services/               # lib/services (ahora llaman a la API FastAPI)
├── utils/                  # lib/utils (lógica de las tareas, mismos nombres)
├── widgets/                # lib/widgets (menú lateral, diálogos, etc.)
├── screens/                # lib/screens
│   ├── HomeScreen.vue
│   ├── LoginScreen.vue
│   ├── RegisterScreen.vue
│   ├── ChangePasswordScreen.vue
│   ├── ResetPasswordScreen.vue
│   ├── MovementsScreen.vue
│   ├── PresupuestoCategoriaScreen.vue
│   └── HistoryScreen.vue
└── assets/icons/           # antes assets/icons
tests/unit/                 # antes test/ (los mismos casos, en Vitest)
e2e/                        # antes integration_test/ (en Playwright)
```

## Correr

```bash
pnpm install
pnpm dev      # http://localhost:5173 (las llamadas a /api van al backend en :8000)
pnpm build    # genera dist/
```

## Pruebas

```bash
pnpm test                 # pruebas unitarias
pnpm semilla              # deja la base budget_e2e con Martita y Pablo
pnpm test:e2e --headed    # E2E: levanta backend y frontend de prueba solo
```

Los usuarios de prueba y los detalles están en el [README principal](../README.md#pruebas-e2e-playwright).
