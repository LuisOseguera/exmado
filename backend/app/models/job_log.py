import enum
import uuid
from datetime import datetime

from sqlalchemy import (
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


class LogLevel(str, enum.Enum):
    """Niveles de logging"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class JobLog(Base):
    """
    Modelo para almacenar logs detallados de cada job.
    Útil para debugging y para mostrar al usuario qué está pasando.
    """

    __tablename__ = "job_logs"

    # Identificadores
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    # Log info
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False)
    message = Column(Text, nullable=False)

    # Contexto adicional
    record_id = Column(
        String, ForeignKey("job_records.id", ondelete="SET NULL"), nullable=True
    )
    excel_row_number = Column(Integer, nullable=True)  # Para referencias rápidas
    details = Column(Text, nullable=True)  # Información adicional en texto

    # Relaciones
    job = relationship("Job", back_populates="logs")

    def __repr__(self):
        return f"<JobLog {self.id} - {self.level.value} - {self.message[:50]}>"

    def to_dict(self):
        """Convierte el log a diccionario para API responses"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "message": self.message,
            "record_id": self.record_id,
            "excel_row_number": self.excel_row_number,
            "details": self.details,
        }

    @classmethod
    def create_log(
        cls,
        job_id: str,
        level: LogLevel,
        message: str,
        record_id: str = None,
        excel_row_number: int = None,
        details: str = None,
    ):
        """
        Helper method para crear logs fácilmente.

        Uso:
            JobLog.create_log(
                job_id=job.id,
                level=LogLevel.INFO,
                message="Iniciando descarga",
                excel_row_number=15
            )
        """
        return cls(
            job_id=job_id,
            level=level,
            message=message,
            record_id=record_id,
            excel_row_number=excel_row_number,
            details=details,
        )
