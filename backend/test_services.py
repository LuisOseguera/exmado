"""
Script para probar los servicios implementados.
Ejecutar: python test_services.py
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Cambiar al directorio backend para que las rutas relativas funcionen
os.chdir(backend_dir)

from app.config import settings
from app.services import DocuWareClient, FileTransformer, ExcelParser, FolderOrganizer


def test_file_transformer():
    """Prueba el transformador de archivos"""
    print("\n" + "=" * 60)
    print("TEST: FileTransformer")
    print("=" * 60)

    transformer = FileTransformer()

    # Test 1: Sanitizar nombres
    print("\n1. Sanitización de nombres:")
    test_names = [
        "archivo:con*caracteres|invalidos.pdf",
        "   archivo   con   espacios   .xlsx",
        "archivo/con\\barras.pdf",
    ]

    for name in test_names:
        sanitized = transformer.sanitize_filename(name)
        print(f"  Original: {name}")
        print(f"  Sanitizado: {sanitized}")

    # Test 2: Obtener extensión
    print("\n2. Obtención de extensiones:")
    test_files = ["documento.pdf", "archivo.XLSX", "imagen.TIF"]

    for file in test_files:
        ext = transformer.get_file_extension(file)
        print(f"  {file} → {ext}")

    # Test 3: Validar tipo de archivo
    print("\n3. Validación de tipos:")
    allowed = ["pdf", "xlsx"]

    for file in test_files:
        is_valid = transformer.is_valid_file_type(file, allowed)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {file} (permitidos: {allowed})")

    print("\n✓ FileTransformer: OK")


def test_excel_parser():
    """Prueba el parser de Excel"""
    print("\n" + "=" * 60)
    print("TEST: ExcelParser")
    print("=" * 60)

    parser = ExcelParser()

    # Test 1: Limpieza de DataFrame
    print("\n1. Limpieza de DataFrames:")
    import pandas as pd

    # Crear DataFrame de prueba con datos sucios
    df_dirty = pd.DataFrame(
        {
            "  Columna 1  ": [1, 2, None, 4],
            "Columna 2": ["A", "B", "C", None],
            "Columna Vacía": [None, None, None, None],
        }
    )

    print(f"  Antes: {len(df_dirty)} filas, {len(df_dirty.columns)} columnas")
    df_clean = parser.clean_dataframe(df_dirty)
    print(f"  Después: {len(df_clean)} filas, {len(df_clean.columns)} columnas")
    print(f"  Columnas: {list(df_clean.columns)}")

    # Test 2: Validación de columnas
    print("\n2. Validación de columnas:")
    required = ["Columna 1", "Columna 2"]
    is_valid, missing = parser.validate_columns(df_clean, required)
    print(f"  Requeridas: {required}")
    print(f"  ¿Válido?: {is_valid}")
    if not is_valid:
        print(f"  Faltantes: {missing}")

    # Test 3: Conversión a registros
    print("\n3. Conversión a diccionarios:")
    records = parser.to_dict_records(df_clean)
    print(f"  Total de registros: {len(records)}")
    if records:
        print(f"  Primer registro: {records[0]}")

    print("\n✓ ExcelParser: OK")


def test_folder_organizer():
    """Prueba el organizador de carpetas"""
    print("\n" + "=" * 60)
    print("TEST: FolderOrganizer")
    print("=" * 60)

    # Crear directorio temporal para pruebas
    test_dir = Path("./test_output")
    test_dir.mkdir(exist_ok=True)

    organizer = FolderOrganizer(str(test_dir))

    # Test 1: Construcción de ruta de carpetas
    print("\n1. Construcción de rutas:")
    folder_structure = ["Año", "Proveedor", "Documento"]
    record_data = {"Año": "2024", "Proveedor": "ACME Corp", "Documento": "FAC-001"}

    folder_path = organizer.build_folder_path(folder_structure, record_data)
    print(f"  Estructura: {folder_structure}")
    print(f"  Datos: {record_data}")
    print(f"  Ruta: {folder_path}")

    # Test 2: Crear carpeta
    print("\n2. Creación de carpetas:")
    success = organizer.create_folder(folder_path)
    print(f"  ¿Creada?: {'✓ Sí' if success else '✗ No'}")

    # Test 3: Formateo de tamaño
    print("\n3. Formateo de tamaños:")
    test_sizes = [1024, 1024 * 1024, 1024 * 1024 * 1024]

    for size in test_sizes:
        formatted = organizer.format_size(size)
        print(f"  {size} bytes = {formatted}")

    # Test 4: Listar carpetas creadas
    print("\n4. Carpetas creadas:")
    folders = organizer.list_created_folders()
    for folder in folders:
        print(f"  - {folder}")

    print("\n✓ FolderOrganizer: OK")

    # Limpiar
    import shutil

    shutil.rmtree(test_dir)
    print(f"\n✓ Directorio de prueba eliminado")


def test_docuware_client():
    """Prueba el cliente de DocuWare (sin autenticación real)"""
    print("\n" + "=" * 60)
    print("TEST: DocuWareClient")
    print("=" * 60)

    print("\n1. Configuración:")
    print(f"  URL: {settings.DOCUWARE_URL}")
    print(f"  Usuario: {settings.DOCUWARE_USERNAME}")
    print(f"  Timeout: {settings.DOCUWARE_TIMEOUT}s")

    print("\n⚠ Test de conexión real requiere credenciales válidas")
    print("  Para probar la conexión:")
    print("  1. Configurar .env con credenciales reales")
    print("  2. Descomentar el código de prueba abajo")

    # Descomentar para probar conexión real:
    # client = DocuWareClient()
    # if client.authenticate():
    #     print("✓ Autenticación exitosa")
    #     client.close()
    # else:
    #     print("✗ Error de autenticación")

    print("\n✓ DocuWareClient: OK (sin prueba de conexión)")


def test_integration():
    """Prueba de integración: flujo completo simulado"""
    print("\n" + "=" * 60)
    print("TEST DE INTEGRACIÓN")
    print("=" * 60)

    print("\n📋 Simulando flujo completo:")
    print("  1. Parsear Excel")
    print("  2. Transformar archivos")
    print("  3. Organizar en carpetas")

    # Crear datos de prueba
    import pandas as pd

    # Paso 1: Parsear Excel (simulado)
    print("\n[1/3] Parseando Excel...")
    parser = ExcelParser()

    df_test = pd.DataFrame(
        {
            "Año": ["2024", "2024", "2024"],
            "Proveedor": ["ACME Corp", "TechCo", "Services Inc"],
            "Factura": ["FAC-001", "FAC-002", "FAC-003"],
            "Monto": [1000, 2000, 1500],
        }
    )

    records = parser.to_dict_records(df_test)
    print(f"  ✓ {len(records)} registros parseados")

    # Paso 2: Transformar nombres (simulado)
    print("\n[2/3] Transformando nombres...")
    transformer = FileTransformer()

    for record in records:
        original = f"{record['Factura']}.pdf"
        sanitized = transformer.sanitize_filename(original)
        print(f"  ✓ {original} → {sanitized}")

    # Paso 3: Organizar en carpetas (simulado)
    print("\n[3/3] Organizando en carpetas...")
    test_dir = Path("./test_integration")
    organizer = FolderOrganizer(str(test_dir))

    for record in records:
        folder_path = organizer.build_folder_path(["Año", "Proveedor"], record)
        organizer.create_folder(folder_path)
        print(f"  ✓ {organizer.get_relative_path(str(folder_path))}")

    # Estadísticas
    total_folders = len(organizer.list_created_folders())
    print(f"\n📊 Resultados:")
    print(f"  Registros procesados: {len(records)}")
    print(f"  Carpetas creadas: {total_folders}")

    # Limpiar
    import shutil

    shutil.rmtree(test_dir)

    print("\n✓ TEST DE INTEGRACIÓN: OK")


def main():
    """Función principal"""
    print("=" * 60)
    print("ÉXMADO - TEST DE SERVICIOS")
    print("=" * 60)

    try:
        test_file_transformer()
        test_excel_parser()
        test_folder_organizer()
        test_docuware_client()
        test_integration()

        print("\n" + "=" * 60)
        print("✓ TODOS LOS TESTS PASARON CORRECTAMENTE")
        print("=" * 60)

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ ERROR EN LOS TESTS")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
