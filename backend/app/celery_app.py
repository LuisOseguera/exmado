"""
Configuración de Celery para procesamiento asíncrono.
"""

from celery import Celery

from app.config import settings

# Crear aplicación Celery
celery_app = Celery(
    "exmado",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.download_task"],  # Importar módulos de tareas
)

# Configuración de Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Tegucigalpa",  # Ajustar a tu zona horaria
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.JOB_TIMEOUT,  # Timeout máximo por tarea
    worker_prefetch_multiplier=1,  # Procesar una tarea a la vez
    worker_max_tasks_per_child=50,  # Reiniciar worker cada 50 tareas
)

# Configuración de routing (opcional, para tareas específicas)
celery_app.conf.task_routes = {
    "app.tasks.download_task.*": {"queue": "downloads"},
}
