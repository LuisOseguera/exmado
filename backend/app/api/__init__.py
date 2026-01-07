"""
Módulo de API REST.
Contiene todos los endpoints de la aplicación.
"""

from app.api import deps, docuware, excel, jobs, websocket

__all__ = [
    "deps",
    "jobs",
    "excel",
    "docuware",
    "websocket",
]
