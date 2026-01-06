"""
Servicio para organizar archivos descargados en estructura de carpetas.
Crea carpetas dinámicas basadas en datos del Excel.
"""

import os
from pathlib import Path
from typing import Any

from loguru import logger

from app.services.file_transformer import FileTransformer


class FolderOrganizer:
    """Organizador de archivos en estructura de carpetas dinámica"""

    def __init__(self, base_output_dir: str):
        """
        Inicializa el organizador.

        Args:
            base_output_dir: Directorio base donde se crearán las carpetas
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def build_folder_path(
        self, folder_structure: list[str], record_data: dict[str, Any]
    ) -> Path:
        """
        Construye la ruta de carpeta basándose en la estructura definida.

        Args:
            folder_structure: Lista de campos que definen la estructura
                Ejemplo: ["Año", "Proveedor", "Documento"]
            record_data: Diccionario con los datos del registro
                Ejemplo: {"Año": "2024", "Proveedor": "ACME", "Documento": "001"}

        Returns:
            Path objeto con la ruta completa

        Ejemplo:
            folder_structure = ["Año", "Proveedor"]
            record_data = {"Año": "2024", "Proveedor": "ACME Corp"}
            → base_output_dir/2024/ACME Corp/
        """
        folder_path = self.base_output_dir

        for field in folder_structure:
            if field in record_data:
                value = str(record_data[field])
                # Sanitizar el valor para nombre de carpeta
                sanitized = FileTransformer.sanitize_filename(value)
                folder_path = folder_path / sanitized
            else:
                logger.warning(f"⚠ Campo '{field}' no encontrado en datos del registro")
                # Usar placeholder
                folder_path = folder_path / f"[{field}_no_disponible]"

        return folder_path

    def create_folder(self, folder_path: Path) -> bool:
        """
        Crea una carpeta y sus padres si no existen.

        Args:
            folder_path: Ruta de la carpeta a crear

        Returns:
            True si se creó exitosamente o ya existía
        """
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"✓ Carpeta creada/verificada: {folder_path}")
            return True
        except Exception as e:
            logger.error(f"✗ Error al crear carpeta {folder_path}: {str(e)}")
            return False

    def organize_file(
        self,
        source_file: str,
        folder_structure: list[str],
        record_data: dict[str, Any],
        rename_pattern: str | None = None,
        copy_instead_of_move: bool = False,
    ) -> str | None:
        """
        Organiza un archivo en la estructura de carpetas.

        Args:
            source_file: Ruta del archivo a organizar
            folder_structure: Lista de campos para estructura de carpetas
            record_data: Datos del registro para construir la ruta
            rename_pattern: Patrón para renombrar (opcional)
            copy_instead_of_move: Si True, copia en lugar de mover

        Returns:
            Ruta del archivo en su nueva ubicación o None si hay error
        """
        try:
            source_path = Path(source_file)

            if not source_path.exists():
                logger.error(f"✗ Archivo fuente no existe: {source_file}")
                return None

            # Construir carpeta destino
            dest_folder = self.build_folder_path(folder_structure, record_data)

            # Crear carpeta si no existe
            if not self.create_folder(dest_folder):
                return None

            # Determinar nombre del archivo
            if rename_pattern:
                # Renombrar según patrón
                new_name = rename_pattern
                for key, value in record_data.items():
                    placeholder = f"{{{key}}}"
                    if placeholder in new_name:
                        clean_value = FileTransformer.sanitize_filename(str(value))
                        new_name = new_name.replace(placeholder, clean_value)

                # Agregar extensión original
                ext = source_path.suffix
                if not new_name.endswith(ext):
                    new_name += ext

                new_name = FileTransformer.sanitize_filename(new_name)
            else:
                # Mantener nombre original
                new_name = source_path.name

            # Verificar si ya existe y generar nombre único
            new_name = FileTransformer.get_unique_filename(dest_folder, new_name)

            dest_path = dest_folder / new_name

            # Mover o copiar archivo
            if copy_instead_of_move:
                import shutil

                shutil.copy2(source_path, dest_path)
                logger.debug(f"✓ Archivo copiado a: {dest_path}")
            else:
                source_path.rename(dest_path)
                logger.debug(f"✓ Archivo movido a: {dest_path}")

            return str(dest_path)

        except Exception as e:
            logger.error(f"✗ Error al organizar archivo: {str(e)}")
            return None

    def organize_multiple_files(
        self,
        files: list[str],
        folder_structure: list[str],
        record_data: dict[str, Any],
        rename_pattern: str | None = None,
    ) -> list[str]:
        """
        Organiza múltiples archivos en la misma estructura.

        Args:
            files: Lista de rutas de archivos a organizar
            folder_structure: Lista de campos para estructura
            record_data: Datos del registro
            rename_pattern: Patrón de renombrado (se agregará _1, _2, etc.)

        Returns:
            Lista de rutas de archivos organizados
        """
        organized_files = []

        for i, file_path in enumerate(files, 1):
            # Si hay rename_pattern y múltiples archivos, agregar sufijo
            if rename_pattern and len(files) > 1:
                # Dividir extensión del patrón
                base_pattern = rename_pattern
                pattern_with_suffix = f"{base_pattern}_{i}"
            else:
                pattern_with_suffix = rename_pattern

            result = self.organize_file(
                source_file=file_path,
                folder_structure=folder_structure,
                record_data=record_data,
                rename_pattern=pattern_with_suffix,
            )

            if result:
                organized_files.append(result)

        logger.info(f"✓ Organizados {len(organized_files)}/{len(files)} archivos")
        return organized_files

    def get_relative_path(self, absolute_path: str) -> str:
        """
        Obtiene la ruta relativa desde el directorio base.

        Args:
            absolute_path: Ruta absoluta del archivo

        Returns:
            Ruta relativa
        """
        try:
            abs_path = Path(absolute_path)
            rel_path = abs_path.relative_to(self.base_output_dir)
            return str(rel_path)
        except ValueError:
            # Si no es relativo al base_dir, retornar absoluto
            return absolute_path

    def get_folder_size(self, folder_path: Path | None = None) -> int:
        """
        Calcula el tamaño total de una carpeta en bytes.

        Args:
            folder_path: Ruta de la carpeta (None para usar base_output_dir)

        Returns:
            Tamaño total en bytes
        """
        if folder_path is None:
            folder_path = self.base_output_dir

        total_size = 0

        try:
            for dirpath, _dirnames, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    if file_path.exists():
                        total_size += file_path.stat().st_size
        except Exception as e:
            logger.error(f"✗ Error al calcular tamaño: {str(e)}")

        return total_size

    def format_size(self, size_bytes: int) -> str:
        """
        Formatea un tamaño en bytes a formato legible.

        Args:
            size_bytes: Tamaño en bytes

        Returns:
            String formateado (ej: "1.5 GB", "250 MB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def list_created_folders(self) -> list[str]:
        """
        Lista todas las carpetas creadas dentro del directorio base.

        Returns:
            Lista de rutas de carpetas (relativas al base_dir)
        """
        folders = []

        try:
            for root, _dirs, _files in os.walk(self.base_output_dir):
                root_path = Path(root)
                if root_path != self.base_output_dir:
                    rel_path = self.get_relative_path(str(root_path))
                    folders.append(rel_path)
        except Exception as e:
            logger.error(f"✗ Error al listar carpetas: {str(e)}")

        return folders

    def count_files_in_folder(self, folder_path: Path | None = None) -> int:
        """
        Cuenta los archivos en una carpeta (recursivamente).

        Args:
            folder_path: Ruta de la carpeta (None para base_output_dir)

        Returns:
            Cantidad de archivos
        """
        if folder_path is None:
            folder_path = self.base_output_dir

        count = 0

        try:
            for _root, _dirs, files in os.walk(folder_path):
                count += len(files)
        except Exception as e:
            logger.error(f"✗ Error al contar archivos: {str(e)}")

        return count


# Uso del organizador:
#
# organizer = FolderOrganizer("/output/facturas")
#
# # Organizar un archivo
# new_path = organizer.organize_file(
#     source_file="/temp/documento.pdf",
#     folder_structure=["Año", "Proveedor", "Documento"],
#     record_data={"Año": "2024", "Proveedor": "ACME", "Documento": "001"},
#     rename_pattern="{Documento}_{Proveedor}"
# )
#
# # Obtener estadísticas
# total_size = organizer.get_folder_size()
# print(f"Tamaño total: {organizer.format_size(total_size)}")
