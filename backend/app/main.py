# Reemplaza a lib/main.dart del lado del servidor: arma la API
import logging  # importa el módulo logging para registrar eventos y mensajes en la terminal

from fastapi import FastAPI  # importa la clase FastAPI para crear la aplicación web
from fastapi.middleware.cors import CORSMiddleware  # importa el middleware para manejar políticas de CORS

from app.config import get_settings  # importa la función para cargar las variables de configuración
from app.routers import analitica, auth, historial, limites, metas, movimientos, presupuestos  # importa los routers de cada módulo de la API

logging.basicConfig(level=logging.INFO)  # configura el nivel de registro de logs a nivel INFO

settings = get_settings()  # obtiene la instancia con la configuración actual
app = FastAPI(  # inicializa la instancia principal de la aplicación FastAPI
    title=f"{settings.app_name} API",  # asigna el título de la documentación de la API
    description="API para registrar movimientos, límites mensuales, presupuestos y metas de ahorro.",  # describe el propósito de la API
    version="2.0.0",  # establece la versión actual de la API
)  # fin de inicialización de FastAPI
app.add_middleware(  # añade el middleware de CORS a la aplicación
    CORSMiddleware,  # clase de middleware de CORS
    allow_origins=settings.allowed_origins,  # define los orígenes permitidos que pueden hacer peticiones (frontend)
    allow_credentials=True,  # permite el envío de cookies o cabeceras de autorización
    allow_methods=["*"],  # permite todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # permite todas las cabeceras HTTP en las solicitudes
)  # fin de configuración de CORS

for modulo in (auth, movimientos, limites, presupuestos, historial, metas, analitica):  # itera por cada uno de los módulos de rutas
    app.include_router(modulo.router, prefix="/api")  # incluye las rutas de cada módulo anteponiendo el prefijo /api


@app.get("/api/health", tags=["health"])  # endpoint GET de salud de la API accesible en /api/health
def health() -> dict[str, str]:  # función que atiende la comprobación de salud del backend
    return {"status": "ok"}  # retorna un diccionario indicando que el servicio está funcionando correctamente
