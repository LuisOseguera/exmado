"""
Módulo de API REST.
Contiene todos los endpoints de la aplicación.
"""

from app.api import deps, jobs, excel, docuware, websocket

__all__ = [
    "deps",
    "jobs",
    "excel",
    "docuware",
    "websocket",
]
