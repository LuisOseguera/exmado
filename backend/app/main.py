"""
Punto de Entrada Principal de la Aplicación Backend

Este archivo es el corazón de tu API de FastAPI. Se encarga de inicializar
la aplicación, configurar los middlewares (como CORS), manejar el ciclo de vida,
registrar las rutas de los diferentes módulos y definir manejadores de errores
globales.

Cuando levantás el servicio con Docker, este es el script que Uvicorn ejecuta
para poner en marcha el servidor.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# Importamos nuestros módulos y configuraciones.
# Cada uno de estos representa una sección de tu API.
from app.api import docuware, excel, jobs, websocket
from app.config import ensure_directories, settings
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.

    Esto es lo primero que se ejecuta cuando la aplicación arranca
    y lo último que se ejecuta cuando se detiene. Aquí es donde
    vos ponés la lógica de inicialización y limpieza.
    """
    # Código de arranque (Startup)
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")

    # Nos aseguramos de que los directorios necesarios existan antes de empezar.
    ensure_directories()
    logger.info("Directorios creados y verificados.")

    # Preparamos la base de datos para recibir conexiones.
    init_db()
    logger.info("Base de datos inicializada y lista.")

    yield

    # Código de apagado (Shutdown)
    logger.info("Cerrando la aplicación. ¡Hasta luego!")

# Aquí creamos la instancia principal de la aplicación FastAPI.
# Le pasamos el título, versión y una descripción que se mostrarán
# en la documentación automática de la API (en /docs).
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema para la descarga masiva de documentos desde DocuWare.",
    lifespan=lifespan,
)

# Configuramos el middleware de CORS (Cross-Origin Resource Sharing).
# Esto es crucial para permitir que tu frontend (que corre en otro dominio/puerto)
# pueda hacerle peticiones a este backend sin que el navegador las bloquee.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuramos el logging básico para la aplicación.
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Manejador de excepciones global.

    Si ocurre un error en cualquier parte de la aplicación que no haya sido
    capturado previamente, esta función se encargará de él.
    Esto evita que la aplicación crashee y te permite devolver una
    respuesta de error estandarizada y amigable.
    """
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error Interno del Servidor",
            "message": str(exc) if settings.DEBUG else "Ha ocurrido un error inesperado.",
        },
    )

@app.get("/health", tags=["Salud y Estado"])
async def health_check():
    """
    Endpoint de chequeo de salud.

    Es una buena práctica tener un endpoint como este. Te sirve para verificar
    rápidamente que la API está levantada y respondiendo. Es útil para
    sistemas de monitoreo o para simplemente confirmar que el despliegue funcionó.
    """
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}

@app.get("/", tags=["Salud y Estado"])
async def root():
    """
    Endpoint raíz de la API.

    Ofrece información básica sobre la aplicación y su estado.
    Es la página de bienvenida de tu API.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs_url": "/docs",
        "health_url": "/health",
    }

# --- Registro de Rutas de la API v1 ---
# Aquí es donde organizamos y conectamos todos nuestros endpoints.
# Creamos un "enrutador" principal para la versión 1 de nuestra API.
# Esto te permite versionar tu API en el futuro (ej. /api/v2) de forma ordenada.
api_v1_router = APIRouter(prefix="/api/v1")

# Incluimos los enrutadores de cada módulo dentro del enrutador principal.
# Cada uno tiene su propio prefijo, lo que mantiene el código organizado.
# Por ejemplo, todas las rutas de `jobs.router` empezarán con /api/v1/jobs.
api_v1_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_v1_router.include_router(excel.router, prefix="/excel", tags=["Excel"])
api_v1_router.include_router(docuware.router, prefix="/docuware", tags=["DocuWare"])
api_v1_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

# Finalmente, añadimos el enrutador principal a la aplicación.
app.include_router(api_v1_router)

# Este bloque solo se ejecuta si corrés el script directamente (ej. `python app/main.py`).
# En producción, Uvicorn o Gunicorn se encargan de esto.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
