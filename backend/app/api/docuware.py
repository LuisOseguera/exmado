"""
Endpoints para interactuar con DocuWare.
Permite probar conexión, listar cabinets, diálogos y campos.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from loguru import logger

from app.services import DocuWareClient
from app.api.deps import get_docuware_client
from app.config import settings

router = APIRouter()


@router.get("/test-connection")
def test_connection(client: DocuWareClient = Depends(get_docuware_client)):
    """
    Prueba la conexión con DocuWare.

    **Retorna:**
    - Estado de la conexión
    - Información del servidor

    Este endpoint es útil para verificar que las credenciales son correctas.
    """
    try:
        return {
            "status": "connected",
            "message": "Conexión exitosa con DocuWare",
            "server_url": settings.DOCUWARE_URL,
            "username": settings.DOCUWARE_USERNAME,
        }
    except Exception as e:
        logger.error(f"✗ Error al probar conexión: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error de conexión: {str(e)}",
        )


@router.get("/cabinets")
def list_file_cabinets(client: DocuWareClient = Depends(get_docuware_client)):
    """
    Lista todos los file cabinets (archivadores) disponibles.

    **Retorna:**
    - Lista de cabinets con ID y nombre
    """
    try:
        # Endpoint de DocuWare para listar cabinets
        cabinets_url = f"{settings.DOCUWARE_URL}/FileCabinets"

        response = client.session.get(cabinets_url, timeout=settings.DOCUWARE_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            cabinets = data.get("FileCabinet", [])

            # Extraer información relevante
            cabinet_list = [
                {
                    "id": cabinet.get("Id"),
                    "name": cabinet.get("Name"),
                    "type": cabinet.get("Type"),
                }
                for cabinet in cabinets
            ]

            logger.info(f"✓ Listados {len(cabinet_list)} cabinets")

            return {"cabinets": cabinet_list, "total": len(cabinet_list)}
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al listar cabinets: {response.text}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al listar cabinets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar cabinets: {str(e)}",
        )


@router.get("/cabinets/{cabinet_id}/dialogs")
def list_search_dialogs(
    cabinet_id: str, client: DocuWareClient = Depends(get_docuware_client)
):
    """
    Lista los diálogos de búsqueda disponibles para un cabinet.

    **Parámetros:**
    - cabinet_id: ID del file cabinet

    **Retorna:**
    - Lista de diálogos de búsqueda
    """
    try:
        dialogs_url = f"{settings.DOCUWARE_URL}/FileCabinets/{cabinet_id}/Dialogs"

        response = client.session.get(dialogs_url, timeout=settings.DOCUWARE_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            dialogs = data.get("Dialog", [])

            # Filtrar solo diálogos de búsqueda
            search_dialogs = [
                {
                    "id": dialog.get("Id"),
                    "display_name": dialog.get("DisplayName"),
                    "type": dialog.get("Type"),
                }
                for dialog in dialogs
                if dialog.get("Type") == "Search"
            ]

            logger.info(f"✓ Listados {len(search_dialogs)} diálogos de búsqueda")

            return {
                "cabinet_id": cabinet_id,
                "dialogs": search_dialogs,
                "total": len(search_dialogs),
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al listar diálogos: {response.text}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al listar diálogos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar diálogos: {str(e)}",
        )


@router.get("/cabinets/{cabinet_id}/fields")
def list_cabinet_fields(
    cabinet_id: str, client: DocuWareClient = Depends(get_docuware_client)
):
    """
    Lista los campos (fields) disponibles en un cabinet.

    **Parámetros:**
    - cabinet_id: ID del file cabinet

    **Retorna:**
    - Lista de campos con nombre, tipo y si es requerido

    Útil para mapear columnas del Excel con campos de DocuWare.
    """
    try:
        # Obtener información del cabinet
        cabinet_url = f"{settings.DOCUWARE_URL}/FileCabinets/{cabinet_id}"

        response = client.session.get(cabinet_url, timeout=settings.DOCUWARE_TIMEOUT)

        if response.status_code == 200:
            data = response.json()
            fields = data.get("Fields", [])

            # Extraer información relevante de cada campo
            field_list = [
                {
                    "db_name": field.get("DBName"),
                    "display_name": field.get("DisplayName"),
                    "type": field.get("DWFieldType"),
                    "length": field.get("Length"),
                    "is_required": field.get("IsRequired", False),
                }
                for field in fields
            ]

            logger.info(f"✓ Listados {len(field_list)} campos")

            return {
                "cabinet_id": cabinet_id,
                "fields": field_list,
                "total": len(field_list),
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error al listar campos: {response.text}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al listar campos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar campos: {str(e)}",
        )


@router.post("/search")
def search_documents(
    cabinet_id: str,
    dialog_id: str,
    search_params: Dict[str, Any],
    client: DocuWareClient = Depends(get_docuware_client),
):
    """
    Realiza una búsqueda de documentos en DocuWare.

    **Parámetros:**
    - cabinet_id: ID del file cabinet
    - dialog_id: ID del diálogo de búsqueda
    - search_params: Diccionario con campos y valores de búsqueda

    **Ejemplo de body:**
    ```json
    {
        "cabinet_id": "abc123",
        "dialog_id": "def456",
        "search_params": {
            "AB_PROVEEDOR": "774732",
            "NO__ODC": "78200308"
        }
    }
    ```

    **Retorna:**
    - Lista de documentos encontrados
    """
    try:
        results = client.search_documents(
            cabinet_id=cabinet_id, dialog_id=dialog_id, search_params=search_params
        )

        if results is None:
            return {
                "documents": [],
                "total": 0,
                "message": "No se encontraron documentos",
            }

        # Extraer información básica de cada documento
        documents = [
            {
                "id": doc.get("Id"),
                "fields": doc.get("Fields", []),
                "file_size": doc.get("FileSize"),
                "content_type": doc.get("ContentType"),
            }
            for doc in results
        ]

        return {
            "documents": documents,
            "total": len(documents),
            "cabinet_id": cabinet_id,
            "dialog_id": dialog_id,
        }

    except Exception as e:
        logger.error(f"✗ Error en búsqueda: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}",
        )


@router.get("/documents/{cabinet_id}/{document_id}")
def get_document_info(
    cabinet_id: str,
    document_id: str,
    client: DocuWareClient = Depends(get_docuware_client),
):
    """
    Obtiene información detallada de un documento específico.

    **Parámetros:**
    - cabinet_id: ID del file cabinet
    - document_id: ID del documento

    **Retorna:**
    - Información completa del documento
    """
    try:
        document_info = client.get_document_info(document_id, cabinet_id)

        if document_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Documento {document_id} no encontrado",
            )

        return document_info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al obtener documento: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener documento: {str(e)}",
        )


@router.get("/documents/{cabinet_id}/{document_id}/links")
def get_document_links(
    cabinet_id: str,
    document_id: str,
    client: DocuWareClient = Depends(get_docuware_client),
):
    """
    Obtiene los documentos vinculados (links) de un documento.

    **Parámetros:**
    - cabinet_id: ID del file cabinet
    - document_id: ID del documento padre

    **Retorna:**
    - Lista de documentos vinculados
    """
    try:
        links = client.get_document_links(document_id, cabinet_id)

        if links is None:
            links = []

        return {"document_id": document_id, "links": links, "total": len(links)}

    except Exception as e:
        logger.error(f"✗ Error al obtener links: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener links: {str(e)}",
        )


@router.get("/config")
def get_docuware_config():
    """
    Obtiene la configuración actual de DocuWare (sin credenciales sensibles).

    **Retorna:**
    - URL del servidor
    - Usuario configurado
    - Timeout
    """
    return {
        "server_url": settings.DOCUWARE_URL,
        "username": settings.DOCUWARE_USERNAME,
        "timeout": settings.DOCUWARE_TIMEOUT,
        "configured": bool(settings.DOCUWARE_URL and settings.DOCUWARE_USERNAME),
    }
