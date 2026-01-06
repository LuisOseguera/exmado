"""
Script para iniciar el worker de Celery.

Uso:
    python celery_worker.py

O directamente con Celery:
    celery -A app.celery_app worker --loglevel=info
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.celery_app import celery_app  # noqa: E402

if __name__ == "__main__":
    # Iniciar worker
    celery_app.worker_main(
        [
            "worker",
            "--loglevel=info",
            "--concurrency=2",  # Procesar 2 jobs simultáneamente
            "--pool=solo" if sys.platform == "win32" else "--pool=prefork",
        ]
    )
