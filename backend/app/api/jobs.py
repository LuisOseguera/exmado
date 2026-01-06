"""
Endpoints para gestión de Jobs (trabajos de descarga).
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

router = APIRouter()


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Crea un nuevo job de descarga.

    **Flujo:**
    1. Valida los datos del job
    2. Crea el registro en la base de datos
    3. Retorna el job creado
    4. (La ejecución real se hace en una tarea de Celery)
    """
    try:
        # Crear nuevo job
        new_job = Job(
            user_name=job_data.user_name or current_user,
            excel_file_name=job_data.excel_file_name,
            excel_file_path=f"uploads/{job_data.excel_file_name}",  # TODO: usar path real
            output_directory=job_data.output_directory,
            config=job_data.config.model_dump(),
            status=JobStatus.PENDING,
        )

        db.add(new_job)
        db.commit()
        db.refresh(new_job)

        logger.info(f"✓ Job creado: {new_job.id}")

        # Auto-iniciar si está configurado
        if job_data.config.auto_start:
            from app.tasks.download_task import process_job

            task = process_job.delay(new_job.id)
            new_job.celery_task_id = task.id
            new_job.status = JobStatus.RUNNING
            db.commit()
            db.refresh(new_job)
            logger.info(f"✓ Tarea de Celery encolada: {task.id}")

        return new_job.to_dict()

    except Exception as e:
        logger.error(f"✗ Error al crear job: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear job: {str(e)}",
        ) from e


@router.get("", response_model=JobListResponse)
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: JobStatus | None = None,
    user_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Lista todos los jobs con paginación y filtros opcionales.

    **Parámetros:**
    - skip: Cantidad de registros a saltar (default: 0)
    - limit: Cantidad máxima de registros (default: 50, max: 100)
    - status_filter: Filtrar por estado (opcional)
    - user_filter: Filtrar por usuario (opcional)
    """
    try:
        # Construir query base
        query = db.query(Job)

        # Aplicar filtros
        if status_filter:
            query = query.filter(Job.status == status_filter)

        if user_filter:
            query = query.filter(Job.user_name == user_filter)

        # Contar total
        total = query.count()

        # Aplicar paginación y ordenar por más reciente
        jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

        # Convertir a dict
        jobs_data = [job.to_dict() for job in jobs]

        return {
            "jobs": jobs_data,
            "total": total,
            "page": skip // limit + 1,
            "page_size": limit,
        }

    except Exception as e:
        logger.error(f"✗ Error al listar jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar jobs: {str(e)}",
        ) from e


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene un job específico por su ID.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} no encontrado"
        )

    return job.to_dict()


@router.patch("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, job_update: JobUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un job (principalmente para pausar/reanudar/cancelar).
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} no encontrado"
        )

    try:
        # Actualizar solo los campos proporcionados
        if job_update.status:
            # Validar transiciones de estado válidas
            valid_transitions = {
                JobStatus.PENDING: [JobStatus.RUNNING, JobStatus.CANCELLED],
                JobStatus.RUNNING: [JobStatus.PAUSED, JobStatus.CANCELLED],
                JobStatus.PAUSED: [JobStatus.RUNNING, JobStatus.CANCELLED],
            }

            current_status = job.status
            new_status = job_update.status

            if current_status in valid_transitions:
                if new_status not in valid_transitions[current_status]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Transición inválida: {current_status} → {new_status}",
                    )

            job.status = new_status

            # TODO: Si se pausa/cancela, notificar a la tarea de Celery
            # if new_status == JobStatus.CANCELLED:
            #     celery_app.control.revoke(job.celery_task_id, terminate=True)

        db.commit()
        db.refresh(job)

        logger.info(f"✓ Job actualizado: {job_id}")
        return job.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al actualizar job: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar job: {str(e)}",
        ) from e


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """
    Elimina un job y todos sus registros asociados.

    **ADVERTENCIA:** Esta operación no se puede deshacer.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} no encontrado"
        )

    # Verificar que no esté en ejecución
    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un job en ejecución. Cancélalo primero.",
        )

    try:
        db.delete(job)
        db.commit()
        logger.info(f"✓ Job eliminado: {job_id}")

    except Exception as e:
        logger.error(f"✗ Error al eliminar job: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar job: {str(e)}",
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
    Obtiene los records (registros individuales) de un job.
    """
    # Verificar que el job existe
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} no encontrado"
        )

    # Construir query
    query = db.query(JobRecord).filter(JobRecord.job_id == job_id)

    if status_filter:
        query = query.filter(JobRecord.status == status_filter)

    # Ordenar por número de fila
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
    Obtiene los logs de un job.
    """
    # Verificar que el job existe
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} no encontrado"
        )

    # Construir query
    query = db.query(JobLog).filter(JobLog.job_id == job_id)

    if level_filter:
        query = query.filter(JobLog.level == level_filter)

    total = query.count()

    # Ordenar por timestamp descendente (más reciente primero)
    logs = query.order_by(JobLog.timestamp.desc()).offset(skip).limit(limit).all()

    return {"logs": [log.to_dict() for log in logs], "total": total}


@router.post("/{job_id}/start", response_model=JobResponse)
def start_job(job_id: str, db: Session = Depends(get_db)):
    """
    Inicia la ejecución de un job pendiente.

    Este endpoint encola la tarea de Celery para procesamiento asíncrono.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} no encontrado"
        )

    if job.status != JobStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job debe estar en estado PENDING. Estado actual: {job.status}",
        )

    try:
        # Cambiar estado a RUNNING
        job.status = JobStatus.RUNNING

        # Encolar tarea de Celery
        from app.tasks.download_task import process_job

        task = process_job.delay(job_id)
        job.celery_task_id = task.id

        db.commit()
        db.refresh(job)

        logger.info(f"✓ Job iniciado: {job_id} (Task: {task.id})")
        return job.to_dict()

    except Exception as e:
        logger.error(f"✗ Error al iniciar job: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar job: {str(e)}",
        ) from e
