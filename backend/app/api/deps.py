"""
Dependencies comunes para los endpoints de la API.
"""

from collections.abc import Generator

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import DocuWareClient


def get_docuware_client() -> Generator[DocuWareClient, None, None]:
    """
    Dependency que provee un cliente de DocuWare autenticado.

    Uso en endpoints:
        @app.get("/something")
        def endpoint(client: DocuWareClient = Depends(get_docuware_client)):
            results = client.search_documents(...)
    """
    client = DocuWareClient()

    try:
        # Intentar autenticar
        if not client.authenticate():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No se pudo conectar con DocuWare. Verifica las credenciales.",
            )
        yield client
    finally:
        # Cerrar sesión al terminar el request
        client.close()


def get_current_user() -> str:
    """
    Dependency para obtener el usuario actual.

    NOTA: Por ahora retorna un usuario por defecto.
    En una implementación futura, esto debería:
    - Validar un token JWT
    - Obtener el usuario de la sesión
    - Integrar con sistema de autenticación

    Uso:
        @app.get("/something")
        def endpoint(current_user: str = Depends(get_current_user)):
            print(f"Usuario: {current_user}")
    """
    # TODO: Implementar autenticación real
    return "usuario_sistema"


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency que provee una sesión de base de datos.
    Esta es un alias de get_db() para consistencia en la nomenclatura.

    Uso:
        @app.get("/something")
        def endpoint(db: Session = Depends(get_db_session)):
            jobs = db.query(Job).all()
    """
    return get_db()
