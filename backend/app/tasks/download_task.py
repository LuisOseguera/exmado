"""
Tarea principal de Celery para procesar jobs de descarga.
Esta tarea se ejecuta en segundo plano y procesa documentos de DocuWare.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger

from app.celery_app import celery_app
from app.config import settings
from app.database import SessionLocal
from app.models import Job, JobLog, JobRecord, JobStatus, LogLevel, RecordStatus
from app.services import DocuWareClient, ExcelParser, FileTransformer, FolderOrganizer


@celery_app.task(bind=True, name="app.tasks.download_task.process_job")
def process_job(self, job_id: str):
    """
    Tarea principal que procesa un job de descarga.

    Args:
        job_id: ID del job a procesar

    Esta tarea:
    1. Lee el Excel índice
    2. Busca documentos en DocuWare
    3. Descarga archivos
    4. Aplica transformaciones
    5. Organiza en carpetas
    6. Actualiza progreso en tiempo real
    """
    db = SessionLocal()

    try:
        # Obtener job de la base de datos
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            logger.error(f"✗ Job {job_id} no encontrado")
            return {"status": "error", "message": "Job no encontrado"}

        # Actualizar estado y timestamp
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.commit()

        # Log inicial
        log_entry = JobLog.create_log(
            job_id=job_id,
            level=LogLevel.INFO,
            message="Iniciando procesamiento del job",
        )
        db.add(log_entry)
        db.commit()

        logger.info(f"[Job {job_id}] Iniciando procesamiento")

        # ===== PASO 1: Leer y parsear Excel =====
        excel_result = _process_excel(job, db)
        if not excel_result["success"]:
            _mark_job_as_failed(job, excel_result["error"], db)
            return excel_result

        records_data = excel_result["records"]
        logger.info(f"[Job {job_id}] Excel parseado: {len(records_data)} registros")

        # Actualizar total de registros
        job.total_records = len(records_data)
        db.commit()

        # ===== PASO 2: Procesar cada registro =====
        with DocuWareClient() as dw_client:
            for idx, record_data in enumerate(records_data, 1):
                try:
                    # Verificar si el job fue pausado o cancelado
                    db.refresh(job)
                    if job.status in [JobStatus.PAUSED, JobStatus.CANCELLED]:
                        logger.info(
                            f"[Job {job_id}] Detenido por usuario: {job.status}"
                        )
                        return {"status": job.status.value}

                    # Procesar registro individual
                    _process_record(
                        job=job,
                        record_data=record_data,
                        excel_row_number=idx,
                        dw_client=dw_client,
                        db=db,
                    )

                    # Actualizar progreso
                    job.processed_records = idx
                    db.commit()

                    # TODO: Enviar update por WebSocket
                    # await send_job_progress_update(...)

                    # Log de progreso cada 10 registros
                    if idx % 10 == 0:
                        logger.info(
                            f"[Job {job_id}] Progreso: {idx}/{len(records_data)}"
                        )

                except Exception as e:
                    logger.error(f"[Job {job_id}] Error en registro {idx}: {str(e)}")
                    job.failed_records += 1

                    # Crear log de error
                    error_log = JobLog.create_log(
                        job_id=job_id,
                        level=LogLevel.ERROR,
                        message=f"Error en fila {idx}: {str(e)}",
                        excel_row_number=idx,
                    )
                    db.add(error_log)
                    db.commit()

        # ===== PASO 3: Finalizar job =====
        _finalize_job(job, db)

        logger.info(f"[Job {job_id}] ✓ Completado exitosamente")

        return {
            "status": "completed",
            "job_id": job_id,
            "total_records": job.total_records,
            "successful_records": job.successful_records,
            "failed_records": job.failed_records,
            "total_files_downloaded": job.total_files_downloaded,
        }

    except Exception as e:
        logger.error(f"[Job {job_id}] ✗ Error fatal: {str(e)}")

        if job:
            _mark_job_as_failed(job, str(e), db)

        return {"status": "error", "message": str(e)}

    finally:
        db.close()


def _process_excel(job: Job, db) -> dict[str, Any]:
    """Procesa el archivo Excel índice"""
    try:
        # Log
        log_entry = JobLog.create_log(
            job_id=job.id, level=LogLevel.INFO, message="Leyendo archivo Excel índice"
        )
        db.add(log_entry)
        db.commit()

        # Parsear Excel
        parser = ExcelParser()

        # Determinar sheet si se especificó
        sheet_name = job.config.get("excel_sheet_name")
        sheet_index = job.config.get("excel_sheet_index")

        df, validation = parser.parse_and_validate(
            file_path=job.excel_file_path,
            sheet_name=sheet_name,
            sheet_index=sheet_index,
            filter_headers=True,
        )

        if not validation["is_valid"]:
            return {
                "success": False,
                "error": f"Excel inválido: {validation['errors']}",
            }

        # Aplicar límite en modo prueba
        if job.config.get("test_mode", False):
            limit = job.config.get("test_mode_limit", 10)
            df = df.head(limit)

            log_entry = JobLog.create_log(
                job_id=job.id,
                level=LogLevel.INFO,
                message=f"Modo prueba activado: procesando {len(df)} registros",
            )
            db.add(log_entry)
            db.commit()

        # Convertir a lista de diccionarios
        records = parser.to_dict_records(df)

        return {"success": True, "records": records}

    except Exception as e:
        logger.error(f"Error al procesar Excel: {str(e)}")
        return {"success": False, "error": f"Error al leer Excel: {str(e)}"}


def _process_record(
    job: Job,
    record_data: dict[str, Any],
    excel_row_number: int,
    dw_client: DocuWareClient,
    db,
):
    """Procesa un registro individual (una fila del Excel)"""

    # Crear JobRecord
    job_record = JobRecord(
        job_id=job.id,
        excel_row_number=excel_row_number,
        excel_data=record_data,
        status=RecordStatus.PENDING,
    )
    db.add(job_record)
    db.commit()

    try:
        # ===== Buscar en DocuWare =====
        job_record.status = RecordStatus.SEARCHING
        job_record.started_at = datetime.utcnow()
        db.commit()

        # Construir parámetros de búsqueda
        search_params = {}
        for field_mapping in job.config["search_fields"]:
            excel_col = field_mapping["excel_column"]
            dw_field = field_mapping["docuware_field"]

            if excel_col in record_data:
                search_params[dw_field] = record_data[excel_col]

        # Buscar documentos
        documents = dw_client.search_documents(
            cabinet_id=job.config.get("cabinet_id"),  # TODO: Agregar a config
            dialog_id=job.config["dialog_id"],
            search_params=search_params,
        )

        if not documents or len(documents) == 0:
            job_record.status = RecordStatus.NOT_FOUND
            job_record.completed_at = datetime.utcnow()
            db.commit()
            return

        job_record.status = RecordStatus.FOUND
        job_record.docuware_record_id = documents[0].get("Id")
        db.commit()

        # ===== Descargar archivos =====
        job_record.status = RecordStatus.DOWNLOADING
        db.commit()

        downloaded_files = _download_documents(
            documents=documents,
            job=job,
            record_data=record_data,
            dw_client=dw_client,
            db=db,
        )

        job_record.downloaded_files_count = len(downloaded_files)
        job_record.downloaded_files = downloaded_files

        # ===== Transformar y organizar =====
        job_record.status = RecordStatus.PROCESSING
        db.commit()

        _organize_files(
            downloaded_files=downloaded_files,
            job=job,
            record_data=record_data,
            job_record=job_record,
        )

        # ===== Completar =====
        job_record.status = RecordStatus.COMPLETED
        job_record.completed_at = datetime.utcnow()
        job.successful_records += 1
        job.total_files_downloaded += len(downloaded_files)
        db.commit()

    except Exception as e:
        logger.error(f"Error en registro {excel_row_number}: {str(e)}")
        job_record.status = RecordStatus.FAILED
        job_record.error_message = str(e)
        job_record.completed_at = datetime.utcnow()
        db.commit()
        raise


def _download_documents(
    documents: list, job: Job, record_data: dict, dw_client: DocuWareClient, db
) -> list:
    """Descarga los documentos encontrados"""

    downloaded_files = []
    temp_dir = settings.TEMP_DIR / job.id
    temp_dir.mkdir(parents=True, exist_ok=True)

    for doc in documents:
        try:
            doc_id = doc.get("Id")

            # Descargar documento
            file_content = dw_client.download_document_section(
                document_id=doc_id, cabinet_id=job.config.get("cabinet_id")
            )

            if not file_content:
                continue

            # Guardar temporalmente
            temp_file = temp_dir / f"{doc_id}_document.pdf"
            temp_file.write_bytes(file_content)

            downloaded_files.append(
                {
                    "original_name": f"{doc_id}_document.pdf",
                    "temp_path": str(temp_file),
                    "document_id": doc_id,
                    "file_size": len(file_content),
                }
            )

        except Exception as e:
            logger.error(f"Error al descargar documento {doc_id}: {str(e)}")

    return downloaded_files


def _organize_files(
    downloaded_files: list, job: Job, record_data: dict, job_record: JobRecord
):
    """Organiza los archivos descargados en carpetas"""

    organizer = FolderOrganizer(job.output_directory)
    transformer = FileTransformer()

    organized_files = []

    for file_info in downloaded_files:
        try:
            temp_path = file_info["temp_path"]

            # Aplicar transformaciones si es necesario
            if job.config["transform_rules"].get("tif_to_pdf"):
                if temp_path.endswith(".tif"):
                    temp_path = transformer.convert_tif_to_pdf(temp_path)

            # Organizar archivo
            final_path = organizer.organize_file(
                source_file=temp_path,
                folder_structure=job.config["folder_structure"],
                record_data=record_data,
                rename_pattern=job.config["transform_rules"].get("rename_pattern"),
            )

            if final_path:
                organized_files.append(
                    {
                        "original_name": file_info["original_name"],
                        "saved_path": final_path,
                        "relative_path": organizer.get_relative_path(final_path),
                    }
                )

        except Exception as e:
            logger.error(f"Error al organizar archivo: {str(e)}")

    job_record.output_folder_path = str(Path(job.output_directory))


def _finalize_job(job: Job, db):
    """Finaliza un job exitosamente"""

    if job.failed_records > 0:
        job.status = JobStatus.COMPLETED_WITH_ERRORS
    else:
        job.status = JobStatus.COMPLETED

    job.completed_at = datetime.utcnow()

    # Log final
    log_entry = JobLog.create_log(
        job_id=job.id,
        level=LogLevel.INFO,
        message=f"Job completado: {job.successful_records} exitosos, {job.failed_records} fallidos",
    )
    db.add(log_entry)
    db.commit()


def _mark_job_as_failed(job: Job, error_message: str, db):
    """Marca un job como fallido"""

    job.status = JobStatus.FAILED
    job.error_message = error_message
    job.completed_at = datetime.utcnow()

    log_entry = JobLog.create_log(
        job_id=job.id, level=LogLevel.ERROR, message=f"Job falló: {error_message}"
    )
    db.add(log_entry)
    db.commit()
