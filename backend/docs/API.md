# Éxmado API - Documentación

API REST para el sistema de descarga masiva de documentos desde DocuWare.

## 🚀 Inicio Rápido

### Iniciar el servidor

```bash
cd backend
source venv/Scripts/activate  # Windows Git Bash
# o: source venv/bin/activate  # Linux/Mac
python app/main.py
```

El servidor estará disponible en: **http://localhost:8000**

### Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Desde Swagger UI puedes probar todos los endpoints directamente.

---

## 📚 Endpoints Disponibles

### Health Check

#### `GET /health`

Verifica que la API esté funcionando.

**Response:**

```json
{
  "status": "ok",
  "app": "DocuWare Export Tool",
  "version": "1.0.0"
}
```

---

## 📋 Jobs (Trabajos de Descarga)

### Listar Jobs

#### `GET /api/jobs`

Lista todos los jobs con paginación.

**Query Parameters:**

- `skip` (int): Registros a saltar (default: 0)
- `limit` (int): Máximo de registros (default: 50, max: 100)
- `status_filter` (string): Filtrar por estado
- `user_filter` (string): Filtrar por usuario

**Response:**

```json
{
  "jobs": [...],
  "total": 10,
  "page": 1,
  "page_size": 50
}
```

### Crear Job

#### `POST /api/jobs`

Crea un nuevo job de descarga.

**Request Body:**

```json
{
  "user_name": "usuario",
  "excel_file_name": "requerimiento.xlsx",
  "output_directory": "./output/facturas",
  "config": {
    "cabinet_name": "Facturas",
    "dialog_id": "search-dialog-123",
    "search_fields": [
      {
        "excel_column": "Factura",
        "docuware_field": "INVOICE_NUMBER"
      }
    ],
    "file_filters": ["pdf", "tif"],
    "transform_rules": {
      "tif_to_pdf": true,
      "rename_pattern": "{Factura}_{Proveedor}"
    },
    "folder_structure": ["Año", "Proveedor"],
    "test_mode": true,
    "test_mode_limit": 10
  }
}
```

**Response:** `201 Created`

```json
{
  "id": "abc-123-def",
  "status": "pending",
  "created_at": "2025-12-30T10:00:00",
  ...
}
```

### Obtener Job

#### `GET /api/jobs/{job_id}`

Obtiene información de un job específico.

### Actualizar Job

#### `PATCH /api/jobs/{job_id}`

Actualiza el estado de un job (pausar, reanudar, cancelar).

**Request Body:**

```json
{
  "status": "paused"
}
```

### Eliminar Job

#### `DELETE /api/jobs/{job_id}`

Elimina un job (solo si no está en ejecución).

**Response:** `204 No Content`

### Iniciar Job

#### `POST /api/jobs/{job_id}/start`

Inicia la ejecución de un job pendiente.

### Obtener Records de Job

#### `GET /api/jobs/{job_id}/records`

Lista los registros individuales (filas del Excel) de un job.

### Obtener Logs de Job

#### `GET /api/jobs/{job_id}/logs`

Obtiene los logs de un job.

---

## 📊 Excel

### Subir Excel

#### `POST /api/excel/upload`

Sube y valida un archivo Excel.

**Form Data:**

- `file` (file): Archivo Excel
- `required_columns` (string, opcional): Columnas requeridas (separadas por coma)
- `sheet_name` (string, opcional): Nombre de la hoja
- `sheet_index` (int, opcional): Índice de la hoja

**Ejemplo con curl:**

```bash
curl -X POST "http://localhost:8000/api/excel/upload" \
     -F "file=@requerimiento.xlsx" \
     -F "required_columns=Factura,Proveedor"
```

**Response:**

```json
{
  "is_valid": true,
  "total_rows": 150,
  "columns": ["Año", "Factura", "Proveedor"],
  "errors": [],
  "warnings": [],
  "preview": [...]
}
```

### Validar Excel

#### `POST /api/excel/validate`

Valida un Excel existente en el servidor sin subirlo nuevamente.

### Listar Archivos Subidos

#### `GET /api/excel/list-uploads`

Lista los archivos Excel subidos por el usuario actual.

### Obtener Hojas del Excel

#### `GET /api/excel/sheets/{filename}`

Lista las hojas (sheets) de un archivo Excel.

### Preview de Excel

#### `GET /api/excel/preview/{filename}`

Obtiene una vista previa de un archivo Excel.

**Query Parameters:**

- `sheet_name` (string, opcional)
- `sheet_index` (int, opcional)
- `n_rows` (int): Cantidad de filas (default: 10)

---

## 🔌 DocuWare

### Probar Conexión

#### `GET /api/docuware/test-connection`

Prueba la conexión con DocuWare.

**Response:**

```json
{
  "status": "connected",
  "message": "Conexión exitosa con DocuWare",
  "server_url": "https://...",
  "username": "..."
}
```

### Listar Cabinets

#### `GET /api/docuware/cabinets`

Lista todos los file cabinets disponibles.

**Response:**

```json
{
  "cabinets": [
    {
      "id": "abc-123",
      "name": "Facturas",
      "type": "FileCabinet"
    }
  ],
  "total": 5
}
```

### Listar Diálogos

#### `GET /api/docuware/cabinets/{cabinet_id}/dialogs`

Lista los diálogos de búsqueda de un cabinet.

### Listar Campos

#### `GET /api/docuware/cabinets/{cabinet_id}/fields`

Lista los campos disponibles en un cabinet.

**Response:**

```json
{
  "cabinet_id": "abc-123",
  "fields": [
    {
      "db_name": "INVOICE_NUMBER",
      "display_name": "Número de Factura",
      "type": "Text",
      "is_required": false
    }
  ]
}
```

### Buscar Documentos

#### `POST /api/docuware/search`

Realiza una búsqueda de documentos.

**Request Body:**

```json
{
  "cabinet_id": "abc-123",
  "dialog_id": "def-456",
  "search_params": {
    "AB_PROVEEDOR": "774732",
    "NO__ODC": "78200308"
  }
}
```

### Obtener Documento

#### `GET /api/docuware/documents/{cabinet_id}/{document_id}`

Obtiene información detallada de un documento.

### Obtener Links

#### `GET /api/docuware/documents/{cabinet_id}/{document_id}/links`

Obtiene documentos vinculados.

---

## 🔄 WebSocket

### Conectar a Job

#### `WS /ws/jobs/{job_id}`

WebSocket para recibir actualizaciones en tiempo real.

**Ejemplo en JavaScript:**

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/jobs/abc-123");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Update:", data);
};

// Solicitar estado actual
ws.send(JSON.stringify({ type: "get_status" }));

// Enviar ping
ws.send(JSON.stringify({ type: "ping" }));
```

**Mensajes recibidos:**

1. **Conectado:**

```json
{
  "type": "connected",
  "job_id": "abc-123",
  "current_status": "running",
  "progress": {...}
}
```

2. **Progreso:**

```json
{
  "type": "progress",
  "job_id": "abc-123",
  "processed_records": 50,
  "total_records": 100,
  "progress_percentage": 50.0,
  "current_action": "Descargando...",
  "latest_log": "..."
}
```

3. **Completado:**

```json
{
  "type": "completed",
  "job_id": "abc-123",
  "status": "completed",
  "summary": {...}
}
```

---

## 🧪 Testing

### Ejecutar tests de servicios

```bash
python test_services.py
```

### Ejecutar tests de API

```bash
# Terminal 1: Iniciar API
python app/main.py

# Terminal 2: Ejecutar tests
python test_api.py
```

---

## 🔐 Autenticación

**Estado actual:** Por defecto, todos los endpoints usan `usuario_sistema` como usuario.

**Futuro:** Se implementará autenticación con JWT para usuarios reales.

---

## 📝 Notas

- Todos los endpoints retornan JSON
- Los errores siguen el formato estándar de HTTP
- La paginación usa `skip` y `limit`
- Los timestamps están en formato ISO 8601

---

## 🐛 Errores Comunes

### 503 Service Unavailable en DocuWare

**Causa:** Credenciales inválidas o DocuWare no accesible.  
**Solución:** Verifica las credenciales en `backend/.env`

### 413 Request Entity Too Large

**Causa:** Archivo Excel demasiado grande.  
**Solución:** El límite es 50MB. Dividir el archivo si es necesario.

### 404 Not Found en jobs

**Causa:** Job no existe o fue eliminado.  
**Solución:** Verificar el ID del job con `GET /api/jobs`

---

## 📞 Soporte

Para dudas o problemas, contactar al equipo de desarrollo.
