"""
Endpoints para subir y validar archivos Excel.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pathlib import Path
import shutil
from loguru import logger

from app.config import settings
from app.services import ExcelParser
from app.schemas import ExcelValidationResult
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/upload", response_model=ExcelValidationResult)
async def upload_excel(
    file: UploadFile = File(...),
    required_columns: Optional[str] = Form(None),
    sheet_name: Optional[str] = Form(None),
    sheet_index: Optional[int] = Form(None),
    current_user: str = Depends(get_current_user),
):
    """
    Sube y valida un archivo Excel.
    
    **Parámetros:**
    - file: Archivo Excel a subir
    - required_columns: Columnas requeridas separadas por coma (opcional)
    - sheet_name: Nombre de la hoja a leer (opcional)
    - sheet_index: Índice de la hoja a leer (opcional)
    
    **Retorna:**
    - Resultado de validación con preview de datos
    
    **Ejemplo de uso con curl:**
    ```bash
    curl -X POST "http://localhost:8000/api/excel/upload" \\
         -F "file=@requerimiento.xlsx" \\
         -F "required_columns=Factura,Proveedor"
    ```
    """
    # Validar que es un archivo Excel
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo debe ser Excel (.xlsx o .xls)",
        )

    # Validar tamaño
    file.file.seek(0, 2)  # Ir al final del archivo
    file_size = file.file.tell()
    file.file.seek(0)  # Volver al inicio

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande. Máximo: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.0f}MB",
        )

    try:
        # Crear directorio de uploads si no existe
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Generar nombre único para el archivo
        file_path = settings.UPLOAD_DIR / f"{current_user}_{file.filename}"

        # Guardar archivo
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"✓ Archivo subido: {file_path.name}")

        # Parsear columnas requeridas
        required_cols = None
        if required_columns:
            required_cols = [col.strip() for col in required_columns.split(",")]

        # Validar Excel
        parser = ExcelParser()
        df, validation = parser.parse_and_validate(
            file_path=str(file_path),
            required_columns=required_cols,
            sheet_name=sheet_name,
            sheet_index=sheet_index,
            filter_headers=True,
        )

        # Agregar información del archivo
        validation["file_name"] = file.filename
        validation["file_path"] = str(file_path)
        validation["file_size"] = file_size

        return validation

    except Exception as e:
        logger.error(f"✗ Error al procesar Excel: {str(e)}")
        # Eliminar archivo si hubo error
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar Excel: {str(e)}",
        )


@router.post("/validate", response_model=ExcelValidationResult)
async def validate_excel(
    file_path: str = Form(...),
    required_columns: Optional[str] = Form(None),
    sheet_name: Optional[str] = Form(None),
    sheet_index: Optional[int] = Form(None),
):
    """
    Valida un archivo Excel que ya existe en el servidor.

    **Parámetros:**
    - file_path: Ruta del archivo en el servidor
    - required_columns: Columnas requeridas separadas por coma
    - sheet_name: Nombre de la hoja (opcional)
    - sheet_index: Índice de la hoja (opcional)

    Este endpoint es útil para revalidar archivos sin subirlos nuevamente.
    """
    file_path_obj = Path(file_path)

    if not file_path_obj.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archivo no encontrado: {file_path}",
        )

    try:
        # Parsear columnas requeridas
        required_cols = None
        if required_columns:
            required_cols = [col.strip() for col in required_columns.split(",")]

        # Validar Excel
        parser = ExcelParser()
        df, validation = parser.parse_and_validate(
            file_path=file_path,
            required_columns=required_cols,
            sheet_name=sheet_name,
            sheet_index=sheet_index,
            filter_headers=True,
        )

        return validation

    except Exception as e:
        logger.error(f"✗ Error al validar Excel: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al validar Excel: {str(e)}",
        )


@router.get("/list-uploads")
def list_uploaded_files(current_user: str = Depends(get_current_user)):
    """
    Lista los archivos Excel subidos por el usuario actual.

    **Retorna:**
    - Lista de archivos con nombre, tamaño y fecha
    """
    try:
        if not settings.UPLOAD_DIR.exists():
            return {"files": []}

        files = []
        for file_path in settings.UPLOAD_DIR.glob(f"{current_user}_*.xlsx"):
            stat = file_path.stat()
            files.append(
                {
                    "filename": file_path.name.replace(f"{current_user}_", ""),
                    "full_path": str(file_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }
            )

        # Ordenar por fecha de modificación (más reciente primero)
        files.sort(key=lambda x: x["modified"], reverse=True)

        return {"files": files}

    except Exception as e:
        logger.error(f"✗ Error al listar archivos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar archivos: {str(e)}",
        )


@router.delete("/uploads/{filename}")
def delete_uploaded_file(filename: str, current_user: str = Depends(get_current_user)):
    """
    Elimina un archivo Excel subido.

    **Parámetros:**
    - filename: Nombre del archivo a eliminar
    """
    try:
        # Construir path completo
        file_path = settings.UPLOAD_DIR / f"{current_user}_{filename}"

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Archivo no encontrado: {filename}",
            )

        # Eliminar archivo
        file_path.unlink()
        logger.info(f"✓ Archivo eliminado: {filename}")

        return {"message": f"Archivo {filename} eliminado exitosamente"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al eliminar archivo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar archivo: {str(e)}",
        )


@router.get("/sheets/{filename}")
def get_excel_sheets(filename: str, current_user: str = Depends(get_current_user)):
    """
    Obtiene la lista de hojas (sheets) de un archivo Excel.

    **Parámetros:**
    - filename: Nombre del archivo Excel

    **Retorna:**
    - Lista de nombres de hojas
    """
    try:
        import pandas as pd

        # Construir path completo
        file_path = settings.UPLOAD_DIR / f"{current_user}_{filename}"

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Archivo no encontrado: {filename}",
            )

        # Leer nombres de hojas
        excel_file = pd.ExcelFile(file_path)
        sheets = excel_file.sheet_names

        return {"filename": filename, "sheets": sheets, "total_sheets": len(sheets)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al leer hojas: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al leer hojas del Excel: {str(e)}",
        )


@router.get("/preview/{filename}")
def preview_excel(
    filename: str,
    sheet_name: Optional[str] = None,
    sheet_index: Optional[int] = None,
    n_rows: int = 10,
    current_user: str = Depends(get_current_user),
):
    """
    Obtiene una vista previa de un archivo Excel.

    **Parámetros:**
    - filename: Nombre del archivo
    - sheet_name: Nombre de la hoja (opcional)
    - sheet_index: Índice de la hoja (opcional)
    - n_rows: Cantidad de filas a mostrar (default: 10)
    """
    try:
        # Construir path completo
        file_path = settings.UPLOAD_DIR / f"{current_user}_{filename}"

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Archivo no encontrado: {filename}",
            )

        # Leer Excel
        parser = ExcelParser()
        df = parser.read_excel(str(file_path), sheet_name, sheet_index)

        if df is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo leer el archivo Excel",
            )

        # Limpiar y obtener preview
        df = parser.clean_dataframe(df)
        preview = parser.get_preview(df, n_rows)

        return {
            "filename": filename,
            "total_rows": len(df),
            "columns": list(df.columns),
            "preview": preview,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"✗ Error al obtener preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener preview: {str(e)}",
        )
