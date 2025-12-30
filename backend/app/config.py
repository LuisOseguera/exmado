from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Las variables se pueden sobrescribir con variables de entorno o archivo .env
    """

    # Aplicación
    APP_NAME: str = "DocuWare Export Tool"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Base de datos
    DATABASE_URL: str = "sqlite:///./docuware_export.db"

    # Redis para Celery
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # DocuWare API
    DOCUWARE_URL: str = ""  # e.g., "https://company.docuware.cloud"
    DOCUWARE_USERNAME: Optional[str] = None
    DOCUWARE_PASSWORD: Optional[str] = None
    DOCUWARE_TIMEOUT: int = 30  # segundos

    # Archivos
    UPLOAD_DIR: Path = Path("./uploads")
    OUTPUT_DIR: Path = Path("./output")
    TEMP_DIR: Path = Path("./temp")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Jobs
    MAX_CONCURRENT_JOBS: int = 3
    JOB_TIMEOUT: int = 7200  # 2 horas en segundos
    TEST_MODE_LIMIT: int = 10  # Cantidad de registros en modo prueba

    # WebSocket
    WEBSOCKET_PING_INTERVAL: int = 25
    WEBSOCKET_PING_TIMEOUT: int = 60

    # CORS (para desarrollo local con frontend)
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()


def ensure_directories():
    """Crea los directorios necesarios si no existen"""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)
