"""
Cliente para interactuar con la API de DocuWare.
Adaptado del código existente en docuware-documents-bulk-export.
"""

import requests
from typing import Optional, Dict, List, Any
from loguru import logger
from app.config import settings


class DocuWareClient:
    """Cliente para la API de DocuWare con autenticación y búsqueda"""

    def __init__(self):
        self.base_url = settings.DOCUWARE_URL
        self.username = settings.DOCUWARE_USERNAME
        self.password = settings.DOCUWARE_PASSWORD
        self.timeout = settings.DOCUWARE_TIMEOUT
        self.session: Optional[requests.Session] = None
        self._authenticated = False

    def authenticate(self) -> bool:
        """
        Autentica con DocuWare y crea una sesión.

        Returns:
            bool: True si la autenticación fue exitosa
        """
        try:
            self.session = requests.Session()

            # Endpoint de autenticación de DocuWare
            auth_url = f"{self.base_url}/Account/Logon"

            auth_data = {
                "UserName": self.username,
                "Password": self.password,
                "Organization": "",  # Opcional, depende de tu setup
                "RememberMe": False,
            }

            response = self.session.post(auth_url, json=auth_data, timeout=self.timeout)

            if response.status_code == 200:
                self._authenticated = True
                logger.info("✓ Autenticación exitosa en DocuWare")
                return True
            else:
                logger.error(f"✗ Error de autenticación: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ Error al autenticar: {str(e)}")
            return False

    def _ensure_authenticated(self):
        """Verifica que exista una sesión autenticada"""
        if not self._authenticated or self.session is None:
            raise Exception("Cliente no autenticado. Llamar a authenticate() primero.")

    def search_documents(
        self,
        cabinet_id: str,
        dialog_id: str,
        search_params: Dict[str, Any],
        operation: str = "And",
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Busca documentos en DocuWare usando un diálogo de búsqueda.

        Args:
            cabinet_id: ID del file cabinet
            dialog_id: ID del diálogo de búsqueda
            search_params: Diccionario con campos y valores de búsqueda
                Ejemplo: {"AB_PROVEEDOR": "774732", "NO__ODC": "78200308"}
            operation: Operador lógico ("And" o "Or")

        Returns:
            Lista de documentos encontrados o None si hay error
        """
        self._ensure_authenticated()

        try:
            # Construir URL de búsqueda
            search_url = (
                f"{self.base_url}/FileCabinets/{cabinet_id}/Query/DialogExpression"
            )

            # Construir query conditions
            conditions = []
            for field, value in search_params.items():
                if isinstance(value, list):
                    # Campo con múltiples valores (OR)
                    for v in value:
                        conditions.append({"DBName": field, "Value": [str(v)]})
                else:
                    conditions.append({"DBName": field, "Value": [str(value)]})

            # Payload de búsqueda
            query_payload = {
                "Condition": conditions,
                "Operation": operation,
                "DialogId": dialog_id,
            }

            logger.debug(f"Buscando documentos: {search_params}")

            response = self.session.post(
                search_url, json=query_payload, timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get("Items", [])
                logger.info(
                    f"✓ Búsqueda exitosa: {len(items)} documento(s) encontrado(s)"
                )
                return items
            else:
                logger.error(f"✗ Error en búsqueda: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return None

        except Exception as e:
            logger.error(f"✗ Error al buscar documentos: {str(e)}")
            return None

    def get_document_info(
        self, document_id: str, cabinet_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de un documento.

        Args:
            document_id: ID del documento
            cabinet_id: ID del file cabinet

        Returns:
            Diccionario con información del documento o None si hay error
        """
        self._ensure_authenticated()

        try:
            doc_url = (
                f"{self.base_url}/FileCabinets/{cabinet_id}/Documents/{document_id}"
            )

            response = self.session.get(doc_url, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"✗ Error al obtener info de documento {document_id}: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"✗ Error al obtener info: {str(e)}")
            return None

    def download_document_section(
        self,
        document_id: str,
        cabinet_id: str,
        section_id: str = "1",
        save_path: str = None,
    ) -> Optional[bytes]:
        """
        Descarga una sección (archivo) de un documento.

        Args:
            document_id: ID del documento
            cabinet_id: ID del file cabinet
            section_id: ID de la sección (por defecto "1")
            save_path: Ruta donde guardar el archivo (opcional)

        Returns:
            Contenido del archivo en bytes o None si hay error
        """
        self._ensure_authenticated()

        try:
            download_url = (
                f"{self.base_url}/FileCabinets/{cabinet_id}/"
                f"Documents/{document_id}/FileDownload"
            )

            params = {"targetFileType": "Auto"}

            response = self.session.get(
                download_url, params=params, timeout=self.timeout, stream=True
            )

            if response.status_code == 200:
                content = response.content

                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(content)
                    logger.debug(f"✓ Archivo guardado: {save_path}")

                return content
            else:
                logger.error(f"✗ Error al descargar documento: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"✗ Error al descargar: {str(e)}")
            return None

    def get_document_links(
        self, document_id: str, cabinet_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene documentos vinculados (DocumentLinks).

        Args:
            document_id: ID del documento padre
            cabinet_id: ID del file cabinet

        Returns:
            Lista de documentos vinculados o None si hay error
        """
        self._ensure_authenticated()

        try:
            links_url = (
                f"{self.base_url}/FileCabinets/{cabinet_id}/"
                f"Documents/{document_id}/DocumentLinks"
            )

            response = self.session.get(links_url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                items = data.get("Items", [])
                logger.debug(f"✓ {len(items)} documento(s) vinculado(s) encontrado(s)")
                return items
            else:
                logger.warning(
                    f"No se pudieron obtener links del documento {document_id}"
                )
                return []

        except Exception as e:
            logger.error(f"✗ Error al obtener links: {str(e)}")
            return []

    def close(self):
        """Cierra la sesión de DocuWare"""
        if self.session:
            try:
                # DocuWare logout
                logout_url = f"{self.base_url}/Account/Logoff"
                self.session.post(logout_url, timeout=5)
            except:
                pass
            finally:
                self.session.close()
                self._authenticated = False
                logger.info("✓ Sesión de DocuWare cerrada")

    def __enter__(self):
        """Context manager entry"""
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Uso del cliente:
# with DocuWareClient() as client:
#     results = client.search_documents(
#         cabinet_id="abc123",
#         dialog_id="def456",
#         search_params={"AB_PROVEEDOR": "774732"}
#     )
