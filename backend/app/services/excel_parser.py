"""
Servicio para parsear archivos Excel índice.
Lee y valida la estructura de los archivos Excel que suben los usuarios.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger


class ExcelParser:
    """Parser para archivos Excel con validación de estructura"""

    @staticmethod
    def read_excel(
        file_path: str,
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Lee un archivo Excel y retorna un DataFrame.

        Args:
            file_path: Ruta al archivo Excel
            sheet_name: Nombre de la hoja a leer (opcional)
            sheet_index: Índice de la hoja a leer (opcional, comienza en 0)

        Returns:
            DataFrame de pandas o None si hay error
        """
        try:
            file_path_obj = Path(file_path)

            if not file_path_obj.exists():
                logger.error(f"✗ Archivo no existe: {file_path}")
                return None

            if not file_path_obj.suffix.lower() in [".xlsx", ".xls"]:
                logger.error(f"✗ Archivo no es Excel: {file_path}")
                return None

            # Determinar qué hoja leer
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            elif sheet_index is not None:
                df = pd.read_excel(file_path, sheet_name=sheet_index)
            else:
                df = pd.read_excel(file_path)  # Primera hoja por defecto

            logger.info(f"✓ Excel leído: {len(df)} filas, {len(df.columns)} columnas")
            return df

        except Exception as e:
            logger.error(f"✗ Error al leer Excel: {str(e)}")
            return None

    @staticmethod
    def validate_columns(
        df: pd.DataFrame, required_columns: List[str], case_sensitive: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Valida que el DataFrame tenga las columnas requeridas.

        Args:
            df: DataFrame a validar
            required_columns: Lista de nombres de columnas requeridas
            case_sensitive: Si True, compara nombres exactos

        Returns:
            Tupla (es_válido, columnas_faltantes)
        """
        if not case_sensitive:
            df_columns = [col.lower() for col in df.columns]
            required_columns = [col.lower() for col in required_columns]
        else:
            df_columns = list(df.columns)

        missing_columns = [col for col in required_columns if col not in df_columns]

        if missing_columns:
            logger.warning(f"⚠ Columnas faltantes: {missing_columns}")
            return False, missing_columns

        logger.info(f"✓ Todas las columnas requeridas están presentes")
        return True, []

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia un DataFrame eliminando filas y columnas vacías.

        Args:
            df: DataFrame a limpiar

        Returns:
            DataFrame limpio
        """
        # Eliminar filas completamente vacías
        df = df.dropna(how="all")

        # Eliminar columnas completamente vacías
        df = df.dropna(axis=1, how="all")

        # Eliminar espacios en blanco de los nombres de columnas
        df.columns = df.columns.str.strip()

        # Resetear índice
        df = df.reset_index(drop=True)

        logger.debug(f"✓ DataFrame limpio: {len(df)} filas")
        return df

    @staticmethod
    def filter_header_rows(
        df: pd.DataFrame, header_keywords: List[str] = None
    ) -> pd.DataFrame:
        """
        Filtra filas que parecen ser encabezados.

        Args:
            df: DataFrame a filtrar
            header_keywords: Lista de palabras clave que indican encabezados

        Returns:
            DataFrame filtrado
        """
        if header_keywords is None:
            header_keywords = [
                "purchase order",
                "payee number",
                "orden de compra",
                "proveedor",
                "factura",
                "documento",
                "header",
                "encabezado",
                "columna",
                "field",
            ]

        # Convertir keywords a minúsculas
        header_keywords = [kw.lower() for kw in header_keywords]

        # Función para verificar si una fila es encabezado
        def is_header_row(row):
            row_str = " ".join(
                [str(val).lower() for val in row.values if pd.notna(val)]
            )
            return any(keyword in row_str for keyword in header_keywords)

        # Filtrar filas
        initial_count = len(df)
        df = df[~df.apply(is_header_row, axis=1)]
        filtered_count = initial_count - len(df)

        if filtered_count > 0:
            logger.info(f"✓ Filtradas {filtered_count} fila(s) de encabezado")

        return df.reset_index(drop=True)

    @staticmethod
    def to_dict_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Convierte un DataFrame a lista de diccionarios.

        Args:
            df: DataFrame a convertir

        Returns:
            Lista de diccionarios, uno por fila
        """
        # Convertir NaN a None para JSON
        df = df.where(pd.notna(df), None)

        records = df.to_dict("records")
        logger.debug(f"✓ Convertidos {len(records)} registros")

        return records

    @staticmethod
    def get_column_mapping(
        df: pd.DataFrame, case_sensitive: bool = False
    ) -> Dict[str, str]:
        """
        Genera un mapeo de columnas (nombre original → nombre normalizado).

        Args:
            df: DataFrame
            case_sensitive: Si False, normaliza a minúsculas

        Returns:
            Diccionario {nombre_original: nombre_normalizado}
        """
        mapping = {}

        for col in df.columns:
            original = col
            normalized = col.strip()

            if not case_sensitive:
                normalized = normalized.lower()

            mapping[original] = normalized

        return mapping

    @staticmethod
    def validate_data_types(
        df: pd.DataFrame, column_types: Dict[str, type]
    ) -> Tuple[bool, List[str]]:
        """
        Valida que las columnas tengan los tipos de datos esperados.

        Args:
            df: DataFrame a validar
            column_types: Diccionario {columna: tipo_esperado}
                Ejemplo: {"AB_PROVEEDOR": str, "NO__ODC": int}

        Returns:
            Tupla (es_válido, errores)
        """
        errors = []

        for column, expected_type in column_types.items():
            if column not in df.columns:
                errors.append(f"Columna '{column}' no encontrada")
                continue

            # Intentar convertir al tipo esperado
            try:
                if expected_type == str:
                    df[column] = df[column].astype(str)
                elif expected_type == int:
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                    if df[column].isna().any():
                        errors.append(
                            f"Columna '{column}' contiene valores no numéricos"
                        )
                elif expected_type == float:
                    df[column] = pd.to_numeric(df[column], errors="coerce")
            except Exception as e:
                errors.append(f"Error en columna '{column}': {str(e)}")

        if errors:
            logger.warning(f"⚠ Errores de validación: {errors}")
            return False, errors

        logger.info(f"✓ Tipos de datos validados correctamente")
        return True, []

    @staticmethod
    def get_preview(df: pd.DataFrame, n_rows: int = 5) -> List[Dict[str, Any]]:
        """
        Obtiene una vista previa de las primeras N filas.

        Args:
            df: DataFrame
            n_rows: Cantidad de filas a retornar

        Returns:
            Lista de diccionarios con las primeras N filas
        """
        preview_df = df.head(n_rows)
        return ExcelParser.to_dict_records(preview_df)

    @staticmethod
    def parse_and_validate(
        file_path: str,
        required_columns: List[str] = None,
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None,
        filter_headers: bool = True,
    ) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """
        Método completo que parsea y valida un Excel.

        Args:
            file_path: Ruta al archivo Excel
            required_columns: Columnas requeridas (opcional)
            sheet_name: Nombre de hoja (opcional)
            sheet_index: Índice de hoja (opcional)
            filter_headers: Si True, filtra filas de encabezado

        Returns:
            Tupla (DataFrame, info_validación)
            info_validación contiene: {
                'is_valid': bool,
                'total_rows': int,
                'columns': list,
                'errors': list,
                'warnings': list,
                'preview': list
            }
        """
        validation_info = {
            "is_valid": False,
            "total_rows": 0,
            "columns": [],
            "errors": [],
            "warnings": [],
            "preview": [],
        }

        # 1. Leer Excel
        df = ExcelParser.read_excel(file_path, sheet_name, sheet_index)
        if df is None:
            validation_info["errors"].append("No se pudo leer el archivo Excel")
            return None, validation_info

        # 2. Limpiar DataFrame
        df = ExcelParser.clean_dataframe(df)

        # 3. Filtrar encabezados si se solicita
        if filter_headers:
            df = ExcelParser.filter_header_rows(df)

        # 4. Validar columnas requeridas
        if required_columns:
            is_valid, missing = ExcelParser.validate_columns(df, required_columns)
            if not is_valid:
                validation_info["errors"].append(f"Columnas faltantes: {missing}")
                return df, validation_info

        # 5. Generar info de validación
        validation_info["is_valid"] = True
        validation_info["total_rows"] = len(df)
        validation_info["columns"] = list(df.columns)
        validation_info["preview"] = ExcelParser.get_preview(df, 5)

        if len(df) == 0:
            validation_info["warnings"].append("El archivo no contiene datos")

        logger.info(f"✓ Excel validado exitosamente: {len(df)} registros")

        return df, validation_info


# Uso del parser:
#
# parser = ExcelParser()
# df, validation = parser.parse_and_validate(
#     file_path="requerimiento.xlsx",
#     required_columns=["Factura", "Proveedor"],
#     filter_headers=True
# )
#
# if validation['is_valid']:
#     records = parser.to_dict_records(df)
#     for record in records:
#         print(record)
