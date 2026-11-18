# Reportes de pruebas y cobertura

Medido el 18/11/2026. Todo el código web (backend FastAPI y frontend Vue) se escribió **en el fork**: el proyecto original era Flutter + Supabase.

| Suite | Pruebas | Cobertura | Reporte |
|---|---|---|---|
| **Backend** (pytest, `backend/app`) | 86 pasan | **100 %** de líneas (1054 de 1054) | [cobertura-backend/index.html](cobertura-backend/index.html) |
| **Lógica del frontend** (Vitest, `frontend/src/utils`) | 81 pasan | **100 %** de líneas, sentencias y funciones; 92 % de ramas | [cobertura-frontend/index.html](cobertura-frontend/index.html) |
| **E2E** (Playwright + axe, pantallas `.vue`) | 88 pasan | Recorre todas las pantallas y flujos; axe revisa la accesibilidad de cada una | `frontend/playwright-report` (se genera al correr) |

Las pantallas `.vue` no se miden con cobertura de líneas: las prueban de punta a punta las 88 pruebas E2E, como lo haría una persona en el navegador.

## Cómo volver a generarlos

```bash
# Backend
cd backend
pip install -r requirements-dev.txt
pytest --cov=app --cov-report=term-missing --cov-report=html:../reportes/cobertura-backend

# Lógica del frontend
cd frontend
pnpm test:cobertura

# E2E (necesita PostgreSQL encendido)
cd frontend
pnpm test:e2e
pnpm exec playwright show-report
```

Abre los `index.html` en el navegador para ver, archivo por archivo, qué líneas cubren las pruebas.
