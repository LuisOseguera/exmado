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
- Docker y Docker Compose (para la cola de tareas con Redis)
- Git

## ⚙️ Configuración

Toda la configuración de la aplicación se gestiona a través de variables de entorno.

1.  **Crear el archivo `.env`**:
    ```bash
    cp .env.example .env
    ```
2.  **Editar `.env`**:
    Abre el archivo `.env` y rellena las variables con tus credenciales de DocuWare y la configuración de la base de datos.

## 🚀 Instalación y Ejecución (Método Recomendado: Docker)

El entorno de desarrollo está completamente dockerizado. Con Docker, puedes levantar todos los servicios del backend (API, Worker y Redis) con un solo comando.

### 1. Clonar el Repositorio

Si aún no lo has hecho, clona el proyecto y navega al directorio del backend.
```bash
git clone https://github.com/LuisOseguera/exmado.git
cd exmado/backend
```

### 2. Configurar el Entorno

Copia el archivo de configuración de ejemplo y edítalo con tus credenciales de DocuWare.
```bash
cp .env.example .env
nano .env  # O usa tu editor favorito
```

### 3. Levantar los Servicios

Ejecuta Docker Compose para construir las imágenes e iniciar los contenedores.
```bash
docker-compose up --build
```
-   La primera vez, `--build` es necesario para construir la imagen de la aplicación.
-   Verás los logs de la API y el Worker en tu terminal.
-   Para detener los servicios, presiona `Ctrl+C`.
-   Para ejecutar en segundo plano, usa `docker-compose up -d`.

¡Y eso es todo! El entorno completo del backend estará funcionando.

## ✅ Verificación

1.  **API**: Abre tu navegador en `http://localhost:8000`. Deberías ver un mensaje de bienvenida en formato JSON.
2.  **Documentación Interactiva**: Visita `http://localhost:8000/docs` para ver la documentación de la API generada por Swagger UI, donde puedes probar los endpoints.

## 🔧 Desarrollo

### Base de Datos

- La aplicación utiliza **SQLite** por defecto, creando un archivo `docuware_export.db` en la raíz del backend.
- Para producción, está preparada para usar **PostgreSQL** (requiere configuración en `.env`).
- Para resetear la base de datos, simplemente elimina el archivo `docuware_export.db`.

### Logging

- Los logs de la aplicación se guardan en el directorio `logs/`.
- También se muestran en la consola donde se ejecuta el servidor.

### Testing

Para ejecutar los tests (cuando se implementen):
```bash
pytest tests/
```

## 📝 Estado y Próximos Pasos

El backend está mayormente funcional, con la lógica principal, API y tareas asíncronas implementadas.

- [ ] **Integración WebSocket**: Mejorar la comunicación en tiempo real.
- [ ] **Tests Unitarios**: Aumentar la cobertura de tests para asegurar la fiabilidad.
- [ ] **Documentación de Usuario**: Crear guías detalladas para los usuarios finales.

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
