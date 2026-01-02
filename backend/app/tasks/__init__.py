"""
Módulo de tareas de Celery.
Contiene las tareas asíncronas de la aplicación.
"""

from app.tasks.download_task import process_job

__all__ = [
    "process_job",
]
