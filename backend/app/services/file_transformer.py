"""
Servicio para transformaciones de archivos: conversión TIF a PDF, renombrado, etc.
Adaptado del código existente en docuware-documents-bulk-export.
"""

import os
import re
from pathlib import Path

import img2pdf
from loguru import logger
from PIL import Image


class FileTransformer:
    """Transformador de archivos con soporte para conversión TIF→PDF y renombrado"""

    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 200) -> str:
        """
        Sanitiza un nombre de archivo removiendo caracteres inválidos.

        Args:
            filename: Nombre del archivo a sanitizar
            max_length: Longitud máxima del nombre

        Returns:
            Nombre de archivo sanitizado
        """
        # Reemplazar caracteres inválidos
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, "_", filename)

        # Remover espacios múltiples
        sanitized = re.sub(r"\s+", " ", sanitized)

        # Truncar si es muy largo (conservar extensión)
        if len(sanitized) > max_length:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[: max_length - len(ext)] + ext

        return sanitized.strip()

    @staticmethod
    def convert_tif_to_pdf(
        tif_path: str, delete_original: bool = True
    ) -> str | None:
        """
        Convierte un archivo TIF multipágina a PDF.

        Args:
            tif_path: Ruta al archivo TIF
            delete_original: Si True, elimina el TIF después de convertir

        Returns:
            Ruta al archivo PDF generado o None si hay error
        """
        try:
            tif_path_obj = Path(tif_path)

            if not tif_path_obj.exists():
                logger.error(f"✗ Archivo TIF no existe: {tif_path}")
                return None

            # Generar nombre del PDF
            pdf_path = tif_path_obj.with_suffix(".pdf")

            # Abrir imagen TIF
            with Image.open(tif_path) as img:
                # Verificar si es multipágina
                num_pages = getattr(img, "n_frames", 1)

                if num_pages == 1:
                    # TIF de una sola página
                    if img.mode == "RGBA":
                        img = img.convert("RGB")
                    elif img.mode not in ("RGB", "L"):
                        img = img.convert("RGB")

                    img.save(pdf_path, "PDF", resolution=100.0)
                else:
                    # TIF multipágina - usar img2pdf para mejor resultado
                    with open(pdf_path, "wb") as f:
                        f.write(img2pdf.convert(tif_path))

            logger.info(
                f"✓ Convertido TIF→PDF: {pdf_path.name} ({num_pages} página(s))"
            )

            # Eliminar TIF original si se solicita
            if delete_original:
                tif_path_obj.unlink()
                logger.debug("  ✓ TIF original eliminado")

            return str(pdf_path)

        except Exception as e:
            logger.error(f"✗ Error al convertir TIF a PDF: {str(e)}")
            return None

    @staticmethod
    def get_unique_filename(directory: Path, filename: str) -> str:
        """
        Genera un nombre de archivo único si ya existe.
        Agrega (1), (2), etc. antes de la extensión.

        Args:
            directory: Directorio donde se guardará el archivo
            filename: Nombre deseado del archivo

        Returns:
            Nombre de archivo único
        """
        filepath = directory / filename

        if not filepath.exists():
            return filename

        # Separar nombre y extensión
        name, ext = os.path.splitext(filename)
        counter = 1

        while filepath.exists():
            new_filename = f"{name} ({counter}){ext}"
            filepath = directory / new_filename
            counter += 1

        return filepath.name

    @staticmethod
    def rename_with_pattern(file_path: str, pattern: str, data: dict) -> str | None:
        """
        Renombra un archivo usando un patrón con placeholders.

        Args:
            file_path: Ruta actual del archivo
            pattern: Patrón de renombrado. Ej: "{Factura}_{Proveedor}_{Fecha}"
            data: Diccionario con los valores para reemplazar

        Returns:
            Nueva ruta del archivo o None si hay error

        Ejemplo:
            rename_with_pattern(
                "documento.pdf",
                "{Factura}_{Proveedor}",
                {"Factura": "001", "Proveedor": "ACME"}
            )
            → "001_ACME.pdf"
        """
        try:
            file_path_obj = Path(file_path)

            if not file_path_obj.exists():
                logger.error(f"✗ Archivo no existe: {file_path}")
                return None

            # Reemplazar placeholders en el patrón
            new_name = pattern
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                if placeholder in new_name:
                    # Sanitizar el valor
                    clean_value = FileTransformer.sanitize_filename(str(value))
                    new_name = new_name.replace(placeholder, clean_value)

            # Agregar extensión original
            ext = file_path_obj.suffix
            if not new_name.endswith(ext):
                new_name += ext

            # Sanitizar nombre completo
            new_name = FileTransformer.sanitize_filename(new_name)

            # Generar ruta completa
            new_path = file_path_obj.parent / new_name

            # Renombrar
            file_path_obj.rename(new_path)
            logger.debug(f"✓ Archivo renombrado: {new_name}")

            return str(new_path)

        except Exception as e:
            logger.error(f"✗ Error al renombrar archivo: {str(e)}")
            return None

    @staticmethod
    def batch_convert_tif_to_pdf(directory: str, recursive: bool = True) -> int:
        """
        Convierte todos los archivos TIF en un directorio a PDF.

        Args:
            directory: Directorio a procesar
            recursive: Si True, procesa subdirectorios

        Returns:
            Cantidad de archivos convertidos
        """
        directory_path = Path(directory)

        if not directory_path.exists():
            logger.error(f"✗ Directorio no existe: {directory}")
            return 0

        # Buscar archivos TIF
        pattern = "**/*.tif" if recursive else "*.tif"
        tif_files = list(directory_path.glob(pattern))

        logger.info(f"Encontrados {len(tif_files)} archivo(s) TIF")

        converted_count = 0
        for tif_file in tif_files:
            result = FileTransformer.convert_tif_to_pdf(str(tif_file))
            if result:
                converted_count += 1

        logger.info(
            f"✓ Conversión completada: {converted_count}/{len(tif_files)} archivos"
        )
        return converted_count

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        Obtiene la extensión de un archivo (sin el punto).

        Args:
            file_path: Ruta del archivo

        Returns:
            Extensión en minúsculas (ej: "pdf", "xlsx")
        """
        return Path(file_path).suffix.lstrip(".").lower()

    @staticmethod
    def is_valid_file_type(file_path: str, allowed_types: list[str]) -> bool:
        """
        Verifica si un archivo es de un tipo permitido.

        Args:
            file_path: Ruta del archivo
            allowed_types: Lista de extensiones permitidas (sin punto)

        Returns:
            True si el archivo es de un tipo permitido
        """
        ext = FileTransformer.get_file_extension(file_path)
        return ext in [t.lower() for t in allowed_types]


# Uso del transformador:
# transformer = FileTransformer()
#
# # Convertir TIF a PDF
# pdf_path = transformer.convert_tif_to_pdf("documento.tif")
#
# # Renombrar con patrón
# new_path = transformer.rename_with_pattern(
#     "documento.pdf",
#     "{Factura}_{Proveedor}_{Fecha}",
#     {"Factura": "001", "Proveedor": "ACME", "Fecha": "2024"}
# )
