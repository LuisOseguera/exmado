from pathlib import Path
from typing import Any

from pydantic import model_validator
from pydantic_settings import BaseSettings


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
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    @model_validator(mode="before")
    def assemble_celery_urls(cls, values: Any) -> Any:
        """
        Construye las URLs de Celery a partir de la configuración de Redis.
        """
        redis_host = values.get("REDIS_HOST", "localhost")
        redis_port = values.get("REDIS_PORT", 6379)
        redis_db = values.get("REDIS_DB", 0)
        redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"

        if "CELERY_BROKER_URL" not in values or values["CELERY_BROKER_URL"] is None:
            values["CELERY_BROKER_URL"] = redis_url
        if (
            "CELERY_RESULT_BACKEND" not in values
            or values["CELERY_RESULT_BACKEND"] is None
        ):
            values["CELERY_RESULT_BACKEND"] = redis_url

        return values

    # DocuWare API
    DOCUWARE_URL: str = ""  # e.g., "https://company.docuware.cloud"
    DOCUWARE_USERNAME: str | None = None
    DOCUWARE_PASSWORD: str | None = None
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
