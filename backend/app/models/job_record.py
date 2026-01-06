import enum
import uuid

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class RecordStatus(str, enum.Enum):
    """Estados posibles de un registro individual"""

    PENDING = "pending"  # No procesado aún
    SEARCHING = "searching"  # Buscando en DocuWare
    FOUND = "found"  # Encontrado en DocuWare
    NOT_FOUND = "not_found"  # No encontrado en DocuWare
    DOWNLOADING = "downloading"  # Descargando archivos
    PROCESSING = "processing"  # Procesando/transformando archivos
    COMPLETED = "completed"  # Completado exitosamente
    FAILED = "failed"  # Falló


class JobRecord(Base):
    """
    Modelo que representa cada registro/fila del Excel índice.
    Cada fila del Excel se convierte en un JobRecord que trackea su procesamiento individual.
    """

    __tablename__ = "job_records"

    # Identificadores
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    # Información del Excel
    excel_row_number = Column(
        Integer, nullable=False
    )  # Número de fila en el Excel (1-indexed)
    excel_data = Column(JSON, nullable=False)  # Datos de la fila del Excel como JSON
    """
    Ejemplo de excel_data:
    {
        "Factura": "FAC-001",
        "Proveedor": "ACME Corp",
        "Año": "2024",
        "Mes": "12"
    }
    """

    # Información de DocuWare
    docuware_record_id = Column(String, nullable=True)  # ID del documento en DocuWare
    docuware_data = Column(JSON, nullable=True)  # Metadata del documento de DocuWare

    # Estado y timestamps
    status = Column(SQLEnum(RecordStatus), default=RecordStatus.PENDING, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Resultados
    downloaded_files_count = Column(
        Integer, default=0
    )  # Cantidad de archivos descargados
    downloaded_files = Column(JSON, nullable=True)  # Lista de archivos descargados
    """
    Ejemplo de downloaded_files:
    [
        {
            "original_name": "document.tif",
            "saved_name": "FAC-001_ACME.pdf",
            "saved_path": "/output/2024/12/ACME/FAC-001_ACME.pdf",
            "file_type": "pdf",
            "file_size": 123456,
            "transformed": true
        }
    ]
    """

    output_folder_path = Column(
        String, nullable=True
    )  # Carpeta donde se guardaron los archivos

    # Errores
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)  # Detalles adicionales del error

    # Relación con Job
    job = relationship("Job", back_populates="records")

    def __repr__(self):
        return (
            f"<JobRecord {self.id} - Row {self.excel_row_number} - {self.status.value}>"
        )

    def to_dict(self):
        """Convierte el record a diccionario para API responses"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "excel_row_number": self.excel_row_number,
            "excel_data": self.excel_data,
            "docuware_record_id": self.docuware_record_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "downloaded_files_count": self.downloaded_files_count,
            "downloaded_files": self.downloaded_files,
            "output_folder_path": self.output_folder_path,
            "error_message": self.error_message,
        }
