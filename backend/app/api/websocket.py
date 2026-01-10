"""
Módulo de WebSocket para Actualizaciones en Tiempo Real

Este módulo se encarga de toda la comunicación en tiempo real entre el backend
y el frontend. Permite que el frontend se suscriba a las actualizaciones de un
trabajo específico y reciba notificaciones sobre su progreso, finalización o
errores sin tener que estar preguntando (polling) constantemente.
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
    Administrador Central de Conexiones WebSocket.

    Esta clase es como un hub central que mantiene un registro de todas las
    conexiones de clientes activas. Asocia cada conexión a un ID de trabajo
    específico, permitiéndonos enviar mensajes solo a los clientes que están
    interesados en un trabajo particular.
    """
    def __init__(self):
        """Inicializa el manager con un diccionario para guardar las conexiones."""
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        """
        Acepta y registra una nueva conexión WebSocket para un trabajo.
        """
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        self.active_connections[job_id].add(websocket)
        logger.info(f"Nuevo cliente WebSocket conectado al trabajo: {job_id}")

    def disconnect(self, websocket: WebSocket, job_id: str):
        """
        Elimina una conexión WebSocket del registro.
        """
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        logger.info(f"Cliente WebSocket desconectado del trabajo: {job_id}")

    async def broadcast_to_job(self, message: dict, job_id: str):
        """
        Envía un mensaje a todos los clientes suscritos a un trabajo.

        Esta es la función clave que usan las tareas de Celery para notificar
        al frontend sobre el progreso.
        """
        if job_id not in self.active_connections:
            return

        # Hacemos una copia para evitar problemas si el set cambia mientras iteramos.
        connections = list(self.active_connections[job_id])
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"No se pudo enviar mensaje por broadcast al trabajo {job_id}: {e}")
                self.disconnect(connection, job_id)

# Creamos una única instancia global del ConnectionManager para que toda la
# aplicación la comparta.
manager = ConnectionManager()

@router.websocket("/jobs/{job_id}")
async def websocket_job_progress(
    websocket: WebSocket, job_id: str, db: Session = Depends(get_db)
):
    """
    Endpoint de WebSocket para el seguimiento del progreso de un trabajo.

    Cuando un cliente (el frontend) se conecta a esta ruta, se establece una
    comunicación bidireccional. El servidor puede empujar actualizaciones del
    trabajo, y el cliente puede enviar mensajes (como 'ping' o 'get_status').
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        logger.warning(f"Intento de conexión a WebSocket para un trabajo no existente: {job_id}")
        await websocket.close(code=1008, reason=f"El trabajo {job_id} no fue encontrado.")
        return

    await manager.connect(websocket, job_id)
    try:
        # Enviamos un mensaje inicial para confirmar la conexión.
        initial_message = {
            "type": "status_update",
            "job_id": job.id,
            "status": job.status.value,
            "progress": {
                "processed": job.processed_records,
                "total": job.total_records,
                "percentage": job.progress_percentage,
                "successful": job.successful_records,
                "failed": job.failed_records,
            },
        }
        await websocket.send_json(initial_message)

        # Mantenemos la conexión viva, escuchando mensajes del cliente.
        while True:
            try:
                # Esperamos un mensaje del cliente con un tiempo de espera.
                data = await asyncio.wait_for(websocket.receive_text(), timeout=25.0)
                message = json.loads(data)

                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "get_status":
                    db.refresh(job)
                    status_message = {
                        "type": "status_update",
                        "job_id": job.id,
                        "status": job.status.value,
                        "progress": {
                            "processed": job.processed_records,
                            "total": job.total_records,
                            "percentage": job.progress_percentage,
                            "successful": job.successful_records,
                            "failed": job.failed_records,
                        },
                    }
                    await websocket.send_json(status_message)

            except asyncio.TimeoutError:
                # Si no recibimos nada en un tiempo, enviamos un 'heartbeat'
                # para mantener la conexión activa y verificar que sigue viva.
                await websocket.send_json({"type": "heartbeat"})
            except (json.JSONDecodeError, TypeError):
                logger.warning(f"Mensaje no válido recibido por WebSocket: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, job_id)
    except Exception as e:
        logger.error(f"Error inesperado en la conexión WebSocket para el trabajo {job_id}: {e}", exc_info=True)
        manager.disconnect(websocket, job_id)


# --- Funciones Auxiliares para Celery ---
# Estas funciones son llamadas desde las tareas de Celery (que se ejecutan en
# otro proceso) para enviar mensajes a los clientes conectados.

async def send_job_progress_update(
    job_id: str,
    status: JobStatus,
    processed_records: int,
    total_records: int,
    current_action: str | None = None,
    latest_log: str | None = None,
):
    """
    Envía una actualización del progreso de un trabajo a los clientes.
    """
    percentage = (processed_records / total_records * 100) if total_records > 0 else 0
    message = {
        "type": "progress",
        "job_id": job_id,
        "status": status.value,
        "processed_records": processed_records,
        "total_records": total_records,
        "progress_percentage": round(percentage, 2),
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
    Notifica a los clientes que un trabajo ha finalizado.
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
    Informa a los clientes que ha ocurrido un error grave en el trabajo.
    """
    message = {"type": "error", "job_id": job_id, "error_message": error_message}
    await manager.broadcast_to_job(message, job_id)
