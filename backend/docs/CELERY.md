# Éxmado - Guía de Celery

Celery maneja el procesamiento asíncrono de jobs de descarga en segundo plano.

## 🚀 Inicio Rápido

### 1. Iniciar Redis

Celery requiere Redis como broker de mensajes:

```bash
# Opción A: Docker (Recomendado)
cd backend
docker-compose up -d

# Opción B: Redis local
# Windows: Descargar desde https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# Mac: brew install redis
redis-server
```

Verificar que Redis está corriendo:

```bash
redis-cli ping
# Debería responder: PONG
```

### 2. Iniciar Celery Worker

**Opción A: Script Helper**

```bash
cd backend
bash start_worker.sh
```

**Opción B: Comando Directo**

```bash
cd backend
source venv/Scripts/activate  # Windows
celery -A app.celery_app worker --loglevel=info --pool=solo
```

**Opción C: Script Python**

```bash
python celery_worker.py
```

### 3. Iniciar API (en otra terminal)

```bash
cd backend
source venv/Scripts/activate
python app/main.py
```

---

## 📊 Flujo de Procesamiento

```
┌─────────────┐
│   Usuario   │
│  Crea Job   │
└──────┬──────┘
       │ POST /api/jobs
       ▼
┌─────────────┐
│  FastAPI    │
│   Guarda    │
│  en SQLite  │
└──────┬──────┘
       │ Encola tarea
       ▼
┌─────────────┐
│    Redis    │
│    Queue    │
└──────┬──────┘
       │ Worker toma tarea
       ▼
┌─────────────┐
│   Celery    │
│   Worker    │ ◄─── process_job(job_id)
└──────┬──────┘
       │
       ├─► Lee Excel
       ├─► Busca en DocuWare
       ├─► Descarga documentos
       ├─► Transforma archivos
       ├─► Organiza en carpetas
       └─► Actualiza progreso
              │
              ▼
       ┌─────────────┐
       │   SQLite    │
       │  (Updates)  │
       └─────────────┘
              │
              ▼
       ┌─────────────┐
       │  WebSocket  │ ──► Frontend
       │  (Optional) │     (Tiempo Real)
       └─────────────┘
```

---

## 🎯 Estados de un Job

```python
PENDING           # Creado, esperando ejecución
  ↓
VALIDATING        # Validando Excel y configuración
  ↓
RUNNING           # En ejecución
  ├─► PAUSED          # Pausado por usuario
  ├─► CANCELLED       # Cancelado por usuario
  ├─► COMPLETED       # Completado exitosamente
  ├─► COMPLETED_WITH_ERRORS  # Completado con algunos errores
  └─► FAILED          # Falló completamente
```

---

## 🔧 Comandos Útiles

### Monitorear Celery

```bash
# Ver tareas en ejecución
celery -A app.celery_app inspect active

# Ver tareas en cola
celery -A app.celery_app inspect scheduled

# Ver estadísticas
celery -A app.celery_app inspect stats

# Ver workers disponibles
celery -A app.celery_app inspect registered
```

### Gestión de Tareas

```bash
# Revocar una tarea
celery -A app.celery_app control revoke <task_id>

# Revocar y terminar
celery -A app.celery_app control revoke <task_id> --terminate

# Purgar todas las tareas en cola
celery -A app.celery_app purge
```

### Flower (Interfaz Web - Opcional)

Flower es una interfaz web para monitorear Celery:

```bash
pip install flower
celery -A app.celery_app flower --port=5555
```

Acceder a: http://localhost:5555

---

## 📝 Configuración

### Variables de Entorno (.env)

```bash
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Jobs
MAX_CONCURRENT_JOBS=3
JOB_TIMEOUT=7200  # 2 horas
```

### Configuración de Celery (app/celery_app.py)

```python
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    timezone='America/Tegucigalpa',
    task_time_limit=7200,  # 2 horas
    worker_prefetch_multiplier=1,
)
```

---

## 🐛 Troubleshooting

### Error: "Connection refused" al iniciar worker

**Causa:** Redis no está corriendo.

**Solución:**

```bash
docker-compose up -d
# o
redis-server
```

### Error: "Task has been revoked"

**Causa:** La tarea fue cancelada manualmente.

**Solución:** Normal si cancelaste el job. Crear uno nuevo.

### Worker no procesa tareas

**Verificar:**

1. Worker está corriendo: `celery -A app.celery_app inspect active`
2. Redis está activo: `redis-cli ping`
3. Ver logs del worker para errores

### Jobs quedan en "running" indefinidamente

**Causa:** Worker se cerró inesperadamente.

**Solución:**

1. Detener el worker
2. Cambiar estado del job manualmente: `PATCH /api/jobs/{id}` → status: "failed"
3. Reiniciar worker

---

## 📊 Monitoring en Producción

### Recomendaciones:

1. **Usar Supervisor o systemd** para mantener el worker corriendo:

```bash
# supervisor.conf
[program:exmado_worker]
command=/path/to/venv/bin/celery -A app.celery_app worker
directory=/path/to/backend
autostart=true
autorestart=true
```

2. **Configurar Redis con persistencia**:

```bash
# redis.conf
appendonly yes
appendfsync everysec
```

3. **Limitar memoria del worker**:

```bash
celery -A app.celery_app worker --max-memory-per-child=500000
```

4. **Logs en archivos**:

```bash
celery -A app.celery_app worker \
    --logfile=/var/log/celery/worker.log \
    --loglevel=info
```

---

## 🧪 Testing de Celery

### Test Manual

```python
# En Python shell o script
from app.tasks.download_task import process_job

# Encolar tarea
result = process_job.delay("job-id-aqui")

# Verificar estado
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE

# Obtener resultado (blocking)
result.get(timeout=10)
```

### Test con API

```bash
# Crear job con auto_start
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "test",
    "excel_file_name": "test.xlsx",
    "output_directory": "./output",
    "config": {
      ...
      "auto_start": true
    }
  }'
```

---

## 🔐 Seguridad

- Redis debería estar solo accesible en localhost
- En producción, configurar autenticación de Redis:
  ```bash
  # redis.conf
  requirepass tu_password_seguro
  ```
- Actualizar CELERY_BROKER_URL:
  ```
  redis://:tu_password_seguro@localhost:6379/0
  ```

---

## 📚 Referencias

- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)
