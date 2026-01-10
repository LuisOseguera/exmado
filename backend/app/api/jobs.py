"""
Endpoints para la Gestión de Trabajos (Jobs)

Este módulo define todas las operaciones de la API relacionadas con los trabajos
de descarga, como crear, listar, obtener detalles, actualizar, eliminar e iniciar
un trabajo.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import Job, JobLog, JobRecord, JobStatus
from app.schemas import (
    JobCreate,
    JobListResponse,
    JobLogsResponse,
    JobRecordResponse,
    JobResponse,
    JobUpdate,
)

# Creamos un enrutador específico para los endpoints de trabajos.
# Esto nos ayuda a mantener el código ordenado y modular.
router = APIRouter()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Crea un nuevo trabajo de descarga.

    Cuando vos mandás una petición a este endpoint, se valida la información,
    se crea un nuevo registro 'Job' en la base de datos y, si está configurado,
    se encola una tarea de Celery para que se ejecute en segundo plano.
    """
    try:
        # Creamos una nueva instancia del modelo Job con la información recibida.
        new_job = Job(
            user_name=job_data.user_name or current_user,
            excel_file_name=job_data.excel_file_name,
            excel_file_path=f"uploads/{job_data.excel_file_name}",
            output_directory=job_data.output_directory,
            config=job_data.config.model_dump(),
            status=JobStatus.PENDING,
        )

        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        logger.info(f"Trabajo creado exitosamente con ID: {new_job.id}")

        # Si el trabajo se configuró para iniciarse automáticamente,
        # encolamos la tarea de Celery de inmediato.
        if job_data.config.auto_start:
            from app.tasks.download_task import process_job

            task = process_job.delay(new_job.id)
            new_job.celery_task_id = task.id
            new_job.status = JobStatus.RUNNING
            db.commit()
            db.refresh(new_job)
            logger.info(f"El trabajo {new_job.id} se ha encolado en Celery con el ID de tarea: {task.id}")

        return new_job.to_dict()

    except Exception as e:
        logger.error(f"Fallo monumental al crear el trabajo: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No pudimos crear el trabajo. Error: {e}",
        ) from e


@router.get("", response_model=JobListResponse)
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: JobStatus | None = None,
    user_filter: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Lista todos los trabajos con paginación y filtros opcionales.

    Este endpoint te permite consultar los trabajos existentes. Podés filtrar
    por estado o por usuario, y paginar los resultados para no sobrecargar
    ni el servidor ni el cliente.
    """
    try:
        query = db.query(Job)

        if status_filter:
            query = query.filter(Job.status == status_filter)

        if user_filter:
            query = query.filter(Job.user_name == user_filter)

        total = query.count()
        jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()
        jobs_data = [job.to_dict() for job in jobs]

        return {
            "jobs": jobs_data,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
        }

    except Exception as e:
        logger.error(f"Fallo al intentar listar los trabajos: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudieron listar los trabajos. Error: {e}",
        ) from e


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene un trabajo específico por su ID.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"El trabajo con ID {job_id} no fue encontrado."
        )

    return job.to_dict()


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, job_update: JobUpdate, db: Session = Depends(get_db)):
    """
    Actualiza el estado de un trabajo (ej: pausar, reanudar, cancelar).
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"El trabajo con ID {job_id} no fue encontrado."
        )

    try:
        if job_update.status:
            # Lógica para validar transiciones de estado.
            # No cualquier estado puede cambiar a cualquier otro.
            valid_transitions = {
                JobStatus.PENDING: [JobStatus.RUNNING, JobStatus.CANCELLED],
                JobStatus.RUNNING: [JobStatus.PAUSED, JobStatus.CANCELLED],
                JobStatus.PAUSED: [JobStatus.RUNNING, JobStatus.CANCELLED],
            }

            current_status = job.status
            new_status = job_update.status

            if current_status in valid_transitions and new_status not in valid_transitions[current_status]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Transición de estado inválida de {current_status.value} a {new_status.value}.",
                )

            job.status = new_status

            # Aquí iría la lógica para interactuar con Celery si se cancela o pausa la tarea.
            # Por ejemplo: `celery_app.control.revoke(job.celery_task_id, terminate=True)`

        db.commit()
        db.refresh(job)
        logger.info(f"Trabajo {job_id} actualizado al estado: {job.status.value}")
        return job.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fallo al actualizar el trabajo {job_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo actualizar el trabajo. Error: {e}",
        ) from e


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """
    Elimina un trabajo y todos sus registros y logs asociados.
    Ojo: Esta operación no se puede deshacer.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"El trabajo con ID {job_id} no fue encontrado."
        )

    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No podés eliminar un trabajo que se está ejecutando. Tenés que cancelarlo primero.",
        )

    try:
        db.delete(job)
        db.commit()
        logger.info(f"Trabajo {job_id} eliminado exitosamente.")

    except Exception as e:
        logger.error(f"Fallo al eliminar el trabajo {job_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo eliminar el trabajo. Error: {e}",
        ) from e


@router.get("/{job_id}/records", response_model=list[JobRecordResponse])
def get_job_records(
    job_id: str,
    status_filter: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Obtiene los registros individuales de un trabajo (las filas del Excel).
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"El trabajo con ID {job_id} no fue encontrado."
        )

    query = db.query(JobRecord).filter(JobRecord.job_id == job_id)

    if status_filter:
        query = query.filter(JobRecord.status == status_filter)

    records = query.order_by(JobRecord.excel_row_number).offset(skip).limit(limit).all()
    return [record.to_dict() for record in records]


@router.get("/{job_id}/logs", response_model=JobLogsResponse)
def get_job_logs(
    job_id: str,
    level_filter: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """
    Obtiene los logs de ejecución de un trabajo.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"El trabajo con ID {job_id} no fue encontrado."
        )

    query = db.query(JobLog).filter(JobLog.job_id == job_id)

    if level_filter:
        query = query.filter(JobLog.level == level_filter)

    total = query.count()
    logs = query.order_by(JobLog.timestamp.desc()).offset(skip).limit(limit).all()

    return {"logs": [log.to_dict() for log in logs], "total": total}


@router.post("/{job_id}/start", response_model=JobResponse)
def start_job(job_id: str, db: Session = Depends(get_db)):
    """
    Inicia la ejecución de un trabajo que está en estado 'pendiente'.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"El trabajo con ID {job_id} no fue encontrado."
        )

    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El trabajo debe estar en estado 'PENDING' para poder iniciarse. Estado actual: {job.status.value}",
        )

    try:
        job.status = JobStatus.RUNNING
        from app.tasks.download_task import process_job

        task = process_job.delay(job_id)
        job.celery_task_id = task.id

        db.commit()
        db.refresh(job)

        logger.info(f"Se inició el trabajo {job_id}. ID de tarea de Celery: {task.id}")
        return job.to_dict()

    except Exception as e:
        logger.error(f"Fallo al iniciar el trabajo {job_id}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No se pudo iniciar el trabajo. Error: {e}",
        ) from e
