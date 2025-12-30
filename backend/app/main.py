from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from loguru import logger

from app.config import settings, ensure_directories
from app.database import init_db

# TODO: Importar los routers cuando estén creados
# from app.api import jobs, docuware, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events de la aplicación.
    Se ejecuta al iniciar y al cerrar la app.
    """
    # Startup
    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")

    # Crear directorios necesarios
    ensure_directories()
    logger.info("Directorios creados/verificados")

    # Inicializar base de datos
    init_db()
    logger.info("Base de datos inicializada")

    yield

    # Shutdown
    logger.info("Cerrando aplicación")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de descarga masiva de documentos desde DocuWare",
    lifespan=lifespan,
)


# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configurar logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# Exception handler global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Maneja todas las excepciones no capturadas"""
    logger.error(f"Error no manejado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint para verificar que la API está funcionando"""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# Root endpoint
@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


# TODO: Incluir routers
# app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
# app.include_router(docuware.router, prefix="/api/docuware", tags=["DocuWare"])
# app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
