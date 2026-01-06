"""
WebSocket para actualizaciones de progreso en tiempo real.
Permite al frontend recibir updates mientras se procesa un job.
"""

import asyncio
import json

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from loguru import logger
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Job, JobStatus

router = APIRouter()


class ConnectionManager:
    """
    Administrador de conexiones WebSocket.
    Mantiene un registro de todas las conexiones activas por job.
    """

    def __init__(self):
        # Diccionario: job_id -> set de WebSocket connections
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """Acepta una nueva conexión WebSocket"""
        await websocket.accept()

        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()

        self.active_connections[job_id].add(websocket)
        logger.info(f"✓ WebSocket conectado para job {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        """Desconecta un WebSocket"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)

            # Si no quedan conexiones para este job, eliminar el entry
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]

        logger.info(f"✓ WebSocket desconectado para job {job_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Envía un mensaje a un WebSocket específico"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"✗ Error al enviar mensaje: {str(e)}")

    async def broadcast_to_job(self, message: dict, job_id: str):
        """
        Envía un mensaje a todos los WebSockets conectados a un job específico.
        Esta es la función que se llamará desde las tareas de Celery.
        """
        if job_id not in self.active_connections:
            return

        # Crear lista de conexiones para evitar modificar el set durante iteración
        connections = list(self.active_connections[job_id])

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"✗ Error al enviar broadcast: {str(e)}")
                # Si falla, desconectar
                self.disconnect(connection, job_id)


# Instancia global del manager
manager = ConnectionManager()


@router.websocket("/jobs/{job_id}")
async def websocket_job_progress(
    websocket: WebSocket, job_id: str, db: Session = Depends(get_db)
):
    """
    WebSocket para recibir actualizaciones de progreso de un job.

    **Conexión:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/jobs/abc-123');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('Progress:', data);
    };
    ```

    **Mensajes recibidos:**
    ```json
    {
        "type": "progress",
        "job_id": "abc-123",
        "status": "running",
        "processed_records": 50,
        "total_records": 100,
        "progress_percentage": 50.0,
        "current_action": "Descargando documento...",
        "latest_log": "Procesando fila 50..."
    }
    ```
    """
    # Verificar que el job existe
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        await websocket.close(code=1008, reason=f"Job {job_id} no encontrado")
        return

    # Conectar WebSocket
    await manager.connect(websocket, job_id)

    try:
        # Enviar estado inicial
        initial_message = {
            "type": "connected",
            "job_id": job_id,
            "message": f"Conectado a job {job_id}",
            "current_status": job.status.value,
            "progress": {
                "processed": job.processed_records,
                "total": job.total_records,
                "percentage": job.progress_percentage,
            },
        }
        await manager.send_personal_message(initial_message, websocket)

        # Mantener la conexión abierta y enviar heartbeat
        while True:
            try:
                # Esperar mensaje del cliente (o timeout cada 25 segundos)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=25.0)

                # Procesar mensaje del cliente si es necesario
                try:
                    message = json.loads(data)

                    # Manejar ping/pong
                    if message.get("type") == "ping":
                        await manager.send_personal_message({"type": "pong"}, websocket)

                    # Manejar solicitud de estado actual
                    elif message.get("type") == "get_status":
                        db.refresh(job)
                        status_message = {
                            "type": "status_update",
                            "job_id": job_id,
                            "status": job.status.value,
                            "progress": {
                                "processed": job.processed_records,
                                "total": job.total_records,
                                "percentage": job.progress_percentage,
                                "successful": job.successful_records,
                                "failed": job.failed_records,
                            },
                        }
                        await manager.send_personal_message(status_message, websocket)

                except json.JSONDecodeError:
                    logger.warning(f"⚠ Mensaje no JSON recibido: {data}")

            except asyncio.TimeoutError:
                # Timeout - enviar heartbeat
                await manager.send_personal_message({"type": "heartbeat"}, websocket)

    except WebSocketDisconnect:
        logger.info(f"Cliente desconectado de job {job_id}")
        manager.disconnect(websocket, job_id)

    except Exception as e:
        logger.error(f"✗ Error en WebSocket: {str(e)}")
        manager.disconnect(websocket, job_id)


async def send_job_progress_update(
    job_id: str,
    status: JobStatus,
    processed_records: int,
    total_records: int,
    current_action: str = None,
    latest_log: str = None,
):
    """
    Función auxiliar para enviar actualizaciones de progreso.

    Esta función debe ser llamada desde las tareas de Celery cuando hay
    actualizaciones en el progreso del job.

    **Ejemplo de uso desde Celery:**
    ```python
    from app.api.websocket import send_job_progress_update

    await send_job_progress_update(
        job_id=job.id,
        status=JobStatus.RUNNING,
        processed_records=50,
        total_records=100,
        current_action="Descargando documento 50...",
        latest_log="Archivo descargado: factura_50.pdf"
    )
    ```
    """
    message = {
        "type": "progress",
        "job_id": job_id,
        "status": status.value,
        "processed_records": processed_records,
        "total_records": total_records,
        "progress_percentage": (
            (processed_records / total_records * 100) if total_records > 0 else 0
        ),
        "current_action": current_action,
        "latest_log": latest_log,
    }

    await manager.broadcast_to_job(message, job_id)


async def send_job_completed(
    job_id: str,
    status: JobStatus,
    total_files_downloaded: int,
    successful_records: int,
    failed_records: int,
):
    """
    Notifica que un job ha completado su ejecución.

    **Ejemplo:**
    ```python
    await send_job_completed(
        job_id=job.id,
        status=JobStatus.COMPLETED,
        total_files_downloaded=250,
        successful_records=248,
        failed_records=2
    )
    ```
    """
    message = {
        "type": "completed",
        "job_id": job_id,
        "status": status.value,
        "summary": {
            "total_files_downloaded": total_files_downloaded,
            "successful_records": successful_records,
            "failed_records": failed_records,
        },
    }

    await manager.broadcast_to_job(message, job_id)


async def send_job_error(job_id: str, error_message: str):
    """
    Notifica que ha ocurrido un error en un job.
    """
    message = {"type": "error", "job_id": job_id, "error_message": error_message}

    await manager.broadcast_to_job(message, job_id)


# Exportar el manager para uso en otras partes del código
__all__ = [
    "router",
    "manager",
    "send_job_progress_update",
    "send_job_completed",
    "send_job_error",
]
