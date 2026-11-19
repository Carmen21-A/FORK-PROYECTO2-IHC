# Reemplaza a lib/main.dart del lado del servidor: arma la API
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analitica, auth, cuenta, historial, limites, metas, movimientos, presupuestos

logging.basicConfig(level=logging.INFO)

settings = get_settings()
app = FastAPI(
    title=f"{settings.app_name} API",
    description="API para registrar movimientos, límites mensuales, presupuestos y metas de ahorro.",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for modulo in (auth, movimientos, limites, presupuestos, historial, metas, analitica, cuenta):
    app.include_router(modulo.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
