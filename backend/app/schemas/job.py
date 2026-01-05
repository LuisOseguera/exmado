from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.job import JobStatus
from app.models.job_record import RecordStatus
from app.models.job_log import LogLevel


# ===== Configuración de Job =====


class SearchFieldMapping(BaseModel):
    """Mapeo entre columna de Excel y campo de DocuWare"""

    excel_column: str = Field(..., description="Nombre de la columna en el Excel")
    docuware_field: str = Field(..., description="Nombre del campo en DocuWare")


class TransformRules(BaseModel):
    """Reglas de transformación de archivos"""

    tif_to_pdf: bool = Field(default=True, description="Convertir archivos TIF a PDF")
    rename_pattern: Optional[str] = Field(
        default=None,
        description="Patrón para renombrar archivos. Ej: '{Factura}_{Proveedor}'",
    )
    lowercase_filenames: bool = Field(
        default=False, description="Convertir nombres a minúsculas"
    )


class JobConfig(BaseModel):
    """Configuración completa de un job"""

    cabinet_name: str = Field(..., description="Nombre del archivador en DocuWare")
    dialog_id: str = Field(..., description="ID del diálogo de búsqueda en DocuWare")

    search_fields: List[SearchFieldMapping] = Field(
        ..., description="Mapeo de campos para búsqueda", min_length=1
    )

    file_filters: List[str] = Field(
        default=["pdf", "tif"], description="Extensiones de archivo a descargar"
    )

    transform_rules: TransformRules = Field(
        default_factory=TransformRules, description="Reglas de transformación"
    )

    folder_structure: List[str] = Field(
        default=[],
        description="Columnas del Excel que definen la estructura de carpetas",
    )

    include_associated_docs: bool = Field(
        default=False, description="Incluir documentos asociados de DocuWare"
    )

    test_mode: bool = Field(
        default=False, description="Ejecutar en modo prueba (solo primeros N registros)"
    )

    test_mode_limit: int = Field(
        default=10, description="Cantidad de registros a procesar en modo prueba"
    )

    auto_start: bool = Field(
        default=False, description="Iniciar automáticamente el job al crearlo"
    )


# ===== Request/Response Schemas =====


class JobCreate(BaseModel):
    """Schema para crear un nuevo job"""

    user_name: str = Field(..., description="Nombre del usuario que crea el job")
    excel_file_name: str = Field(..., description="Nombre del archivo Excel")
    output_directory: str = Field(..., description="Directorio de salida para archivos")
    config: JobConfig = Field(..., description="Configuración del job")


class JobUpdate(BaseModel):
    """Schema para actualizar un job (principalmente para pausar/reanudar/cancelar)"""

    status: Optional[JobStatus] = None


class JobResponse(BaseModel):
    """Schema de respuesta con información de un job"""

    id: str
    user_name: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    excel_file_name: str
    output_directory: str
    total_records: int
    processed_records: int
    successful_records: int
    failed_records: int
    total_files_downloaded: int
    progress_percentage: float
    success_rate: float
    config: JobConfig
    error_message: Optional[str]

    class Config:
        from_attributes = True  # Para compatibilidad con SQLAlchemy models


class JobListResponse(BaseModel):
    """Schema para lista de jobs"""

    jobs: List[JobResponse]
    total: int
    page: int
    page_size: int


# ===== JobRecord Schemas =====


class JobRecordResponse(BaseModel):
    """Schema de respuesta para un registro individual"""

    id: str
    job_id: str
    excel_row_number: int
    excel_data: Dict[str, Any]
    docuware_record_id: Optional[str]
    status: RecordStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    downloaded_files_count: int
    downloaded_files: Optional[List[Dict[str, Any]]]
    output_folder_path: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# ===== JobLog Schemas =====


class JobLogResponse(BaseModel):
    """Schema de respuesta para un log"""

    id: str
    job_id: str
    timestamp: datetime
    level: LogLevel
    message: str
    record_id: Optional[str]
    excel_row_number: Optional[int]
    details: Optional[str]

    class Config:
        from_attributes = True


class JobLogsResponse(BaseModel):
    """Schema para lista de logs"""

    logs: List[JobLogResponse]
    total: int


# ===== Validation Schemas =====


class ExcelValidationResult(BaseModel):
    """Resultado de validación del archivo Excel"""

    is_valid: bool
    total_rows: int
    columns: List[str]
    errors: List[str] = []
    warnings: List[str] = []
    preview_data: List[Dict[str, Any]] = Field(
        default=[], description="Primeras 5 filas como preview"
    )


# ===== Progress Update Schema (para WebSocket) =====


class JobProgressUpdate(BaseModel):
    """Update de progreso para enviar por WebSocket"""

    job_id: str
    status: JobStatus
    processed_records: int
    total_records: int
    progress_percentage: float
    current_record: Optional[int] = None
    current_action: Optional[str] = None
    latest_log: Optional[str] = None
