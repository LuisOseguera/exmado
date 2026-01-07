import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.database import Base


class JobStatus(str, enum.Enum):
    """Estados posibles de un job"""

    PENDING = "pending"  # Creado pero no iniciado
    VALIDATING = "validating"  # Validando Excel y configuración
    RUNNING = "running"  # En ejecución
    PAUSED = "paused"  # Pausado por usuario
    COMPLETED = "completed"  # Completado exitosamente
    COMPLETED_WITH_ERRORS = (
        "completed_with_errors"  # Completado pero con algunos errores
    )
    FAILED = "failed"  # Falló completamente
    CANCELLED = "cancelled"  # Cancelado por usuario


class Job(Base):
    """
    Modelo principal que representa un job de descarga.
    Un job es creado cuando el usuario configura y ejecuta una descarga masiva.
    """

    __tablename__ = "jobs"

    # Identificadores
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_name = Column(String, nullable=False)  # Usuario que creó el job

    # Estado y timestamps
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Archivos
    excel_file_path = Column(String, nullable=False)  # Path al Excel índice
    excel_file_name = Column(String, nullable=False)  # Nombre original del Excel
    output_directory = Column(
        String, nullable=False
    )  # Directorio donde se guardarán los archivos

    # Estadísticas
    total_records = Column(Integer, default=0)  # Total de filas en el Excel
    processed_records = Column(Integer, default=0)  # Registros procesados
    successful_records = Column(Integer, default=0)  # Registros exitosos
    failed_records = Column(Integer, default=0)  # Registros fallidos
    total_files_downloaded = Column(Integer, default=0)  # Total de archivos descargados

    # Configuración del job (almacenada como JSON)
    config = Column(JSON, nullable=False)
    """
    Estructura del JSON de configuración:
    {
        "cabinet_name": "Facturas",
        "dialog_id": "abc123",
        "search_fields": [
            {"excel_column": "Factura", "docuware_field": "INVOICE_NUMBER"},
            {"excel_column": "Proveedor", "docuware_field": "SUPPLIER_NAME"}
        ],
        "file_filters": ["pdf", "tif"],
        "transform_rules": {
            "tif_to_pdf": true,
            "rename_pattern": "{Factura}_{Proveedor}"
        },
        "folder_structure": ["Año", "Mes", "Proveedor"],
        "include_associated_docs": false,
        "test_mode": false,
        "test_mode_limit": 10
    }
    """

    # Error general (si el job falló completamente)
    error_message = Column(Text, nullable=True)

    # Celery task ID (para tracking de la tarea asíncrona)
    celery_task_id = Column(String, nullable=True)

    # Relaciones
    records = relationship(
        "JobRecord", back_populates="job", cascade="all, delete-orphan"
    )
    logs = relationship("JobLog", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job {self.id} - {self.status.value} - {self.excel_file_name}>"

    @property
    def progress_percentage(self) -> float:
        """Calcula el porcentaje de progreso"""
        if self.total_records == 0:
            return 0.0
        return (self.processed_records / self.total_records) * 100

    @property
    def success_rate(self) -> float:
        """Calcula la tasa de éxito"""
        if self.processed_records == 0:
            return 0.0
        return (self.successful_records / self.processed_records) * 100

    def to_dict(self):
        """Convierte el job a diccionario para API responses"""
        return {
            "id": self.id,
            "user_name": self.user_name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "excel_file_name": self.excel_file_name,
            "output_directory": self.output_directory,
            "total_records": self.total_records,
            "processed_records": self.processed_records,
            "successful_records": self.successful_records,
            "failed_records": self.failed_records,
            "total_files_downloaded": self.total_files_downloaded,
            "progress_percentage": self.progress_percentage,
            "success_rate": self.success_rate,
            "config": self.config,
            "error_message": self.error_message,
        }
