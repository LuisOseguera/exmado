"""
Script para probar los endpoints de la API.
Requiere que la API esté corriendo en http://localhost:8000

Ejecutar: python test_api.py
"""

import requests
import json
from pathlib import Path

# URL base de la API
BASE_URL = "http://localhost:8000"


def print_section(title):
    """Imprime un separador de sección"""
    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)


def test_health_check():
    """Prueba el endpoint de health check"""
    print_section("TEST: Health Check")

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    print("✓ Health check: OK")


def test_docuware_config():
    """Prueba el endpoint de configuración de DocuWare"""
    print_section("TEST: DocuWare Config")

    response = requests.get(f"{BASE_URL}/api/docuware/config")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    print("✓ DocuWare config: OK")


def test_docuware_connection():
    """Prueba la conexión con DocuWare"""
    print_section("TEST: DocuWare Connection")

    print("⚠️  Este test requiere credenciales válidas en .env")

    try:
        response = requests.get(f"{BASE_URL}/api/docuware/test-connection")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            print("✓ Conexión exitosa con DocuWare")
        else:
            print(f"✗ Error de conexión: {response.text}")
            print("  Verifica las credenciales en backend/.env")

    except Exception as e:
        print(f"✗ Error: {str(e)}")


def test_list_jobs():
    """Prueba el listado de jobs"""
    print_section("TEST: List Jobs")

    response = requests.get(f"{BASE_URL}/api/jobs")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    print("✓ List jobs: OK")


def test_create_job():
    """Prueba la creación de un job"""
    print_section("TEST: Create Job")

    job_data = {
        "user_name": "test_user",
        "excel_file_name": "test_file.xlsx",
        "output_directory": "./output/test",
        "config": {
            "cabinet_name": "Test Cabinet",
            "dialog_id": "test-dialog-123",
            "search_fields": [
                {"excel_column": "Factura", "docuware_field": "INVOICE_NUMBER"}
            ],
            "file_filters": ["pdf", "xlsx"],
            "transform_rules": {
                "tif_to_pdf": True,
                "rename_pattern": "{Factura}_{Proveedor}",
            },
            "folder_structure": ["Año", "Proveedor"],
            "include_associated_docs": False,
            "test_mode": True,
            "test_mode_limit": 10,
        },
    }

    response = requests.post(f"{BASE_URL}/api/jobs", json=job_data)

    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 201:
        print("✓ Create job: OK")
        return response.json()["id"]
    else:
        print(f"✗ Error al crear job")
        return None


def test_get_job(job_id):
    """Prueba obtener un job específico"""
    print_section(f"TEST: Get Job {job_id}")

    if not job_id:
        print("⏭️  Saltando test (no hay job_id)")
        return

    response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    assert response.status_code == 200
    print("✓ Get job: OK")


def test_excel_upload():
    """Prueba subir un archivo Excel (simulado)"""
    print_section("TEST: Excel Upload")

    print("⚠️  Este test requiere un archivo Excel real")
    print("  Para probar manualmente, usa:")
    print("  curl -X POST http://localhost:8000/api/excel/upload \\")
    print("       -F 'file=@tu_archivo.xlsx' \\")
    print("       -F 'required_columns=Factura,Proveedor'")


def test_api_docs():
    """Verifica que la documentación interactiva esté disponible"""
    print_section("TEST: API Documentation")

    response = requests.get(f"{BASE_URL}/docs")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("✓ Documentación disponible en: http://localhost:8000/docs")
        print("  Abre esa URL en tu navegador para ver la API interactiva")
    else:
        print("✗ Error al acceder a documentación")


def main():
    """Ejecuta todos los tests"""
    print("=" * 60)
    print("ÉXMADO - TEST DE API")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE: La API debe estar corriendo en http://localhost:8000")
    print("  Ejecutar en otra terminal: python app/main.py")
    print()

    try:
        # Tests básicos
        test_health_check()
        test_docuware_config()
        test_api_docs()

        # Tests de endpoints
        test_list_jobs()
        job_id = test_create_job()
        test_get_job(job_id)

        # Tests que requieren configuración adicional
        test_docuware_connection()
        test_excel_upload()

        print("\n" + "=" * 60)
        print("✓ TESTS COMPLETADOS")
        print("=" * 60)
        print("\nPróximos pasos:")
        print("1. Visita http://localhost:8000/docs para ver todos los endpoints")
        print("2. Prueba los endpoints desde la interfaz Swagger")
        print("3. Configura DocuWare en .env para probar la conexión")
        print()

    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 60)
        print("✗ ERROR: No se pudo conectar con la API")
        print("=" * 60)
        print("\nAsegúrate de que la API esté corriendo:")
        print("  cd backend")
        print("  source venv/Scripts/activate  # o venv/bin/activate en Linux/Mac")
        print("  python app/main.py")
        print()

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ ERROR EN LOS TESTS")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
