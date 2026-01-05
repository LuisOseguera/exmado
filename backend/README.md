# Éxmado | DocuWare - Exportación Masiva de Documentos

Sistema de descarga masiva de documentos desde DocuWare con procesamiento asíncrono.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI principal
│   ├── config.py            # Configuración
│   ├── database.py          # Setup de SQLAlchemy
│   ├── models/              # Modelos de base de datos
│   │   ├── __init__.py
│   │   ├── job.py
│   │   ├── job_record.py
│   │   └── job_log.py
│   ├── schemas/             # Schemas de Pydantic
│   │   └── job.py
│   ├── api/                 # Endpoints (próxima fase)
│   ├── services/            # Lógica de negocio (próxima fase)
│   └── tasks/               # Tareas de Celery (próxima fase)
├── tests/
├── requirements.txt
├── .env.example
├── docker-compose.yml
└── README.md
```

## Requisitos Previos

- Python 3.10 o superior
- Docker y Docker Compose (para Redis)
- Git

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/LuisOseguera/exmado.git
cd exmado
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales de DocuWare
nano .env  # o usar tu editor favorito
```

### 5. Iniciar Redis (usando Docker)

```bash
docker-compose up -d
```

O si no usás Docker, instalá Redis localmente:

- **Windows**: Descargar desde https://github.com/microsoftarchive/redis/releases
- **Linux**: `sudo apt-get install redis-server`
- **Mac**: `brew install redis`

### 6. Iniciar la aplicación

```bash
# Terminal 1: Iniciar Redis
docker-compose up -d

# Terminal 2: Iniciar Celery Worker
bash start_worker.sh
# O: celery -A app.celery_app worker --loglevel=info --pool=solo

# Terminal 3: Iniciar FastAPI
python -m app.main
```

## Verificar Instalación

1. Abrí tu navegador en: http://localhost:8000
2. Deberías ver: `{"app": "DocuWare Export Tool", "version": "1.0.0", ...}`
3. Documentación interactiva: http://localhost:8000/docs

## Desarrollo

### Base de datos

La base de datos SQLite se crea automáticamente al iniciar la aplicación en `./docuware_export.db`

Para resetear la base de datos:

```bash
rm docuware_export.db
```

### Logging

Los logs se guardan en:

- Archivo: `./logs/app.log`
- Consola: salida estándar

### Testing (cuando se implemente)

```bash
pytest tests/
```

## 📝 Próximos Pasos de Desarrollo

### ✅ Completado

- [x] Modelos de base de datos
- [x] Schemas de Pydantic
- [x] Servicios de negocio
- [x] Endpoints de API REST
- [x] Tareas de Celery

### 🚧 Pendiente

- [ ] Integración completa WebSocket
- [ ] Tests unitarios
- [ ] Frontend (Fase 2)
- [ ] Documentación de usuario

## Solución de Problemas

### Redis no conecta

- Verificá que Docker esté corriendo: `docker ps`
- Verificá que Redis esté levantado: `docker-compose ps`

### Error al importar módulos

- Verificá que el entorno virtual esté activado
- Reinstalá dependencias: `pip install -r requirements.txt`

### Base de datos corrupta

- Eliminá el archivo y reiniciá: `rm docuware_export.db`

## Contacto

Para dudas o problemas, contactar al equipo de desarrollo.
