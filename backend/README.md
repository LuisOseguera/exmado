# Backend Éxmado

## Descripción General

Este directorio contiene todo el código fuente del servidor backend del proyecto Éxmado. La aplicación está construida con **FastAPI**, un moderno y rápido framework de Python para crear APIs. Se encarga de gestionar la lógica de negocio, la comunicación con la base de datos, la autenticación y el procesamiento de tareas pesadas de forma asíncrona.

## Arquitectura y Tecnologías

El backend sigue una arquitectura modular y escalable, utilizando las siguientes tecnologías clave:

-   **Framework de la API**: [**FastAPI**](https://fastapi.tiangolo.com/)
    -   Provee un sistema de rutas de API robusto y auto-documentado (a través de Swagger y ReDoc).
    -   Utiliza **Pydantic** para la validación y serialización de datos, garantizando la integridad de los datos que entran y salen de la API.

-   **Procesamiento Asíncrono**: [**Celery**](https://docs.celeryq.dev/en/stable/)
    -   Se utiliza para ejecutar tareas que consumen mucho tiempo en segundo plano, como la exportación de documentos desde DocuWare.
    -   Esto evita que la API se bloquee y mejora la experiencia del usuario, permitiendo que el frontend reciba actualizaciones de estado en tiempo real.
    -   Utiliza **Redis** como _message broker_ para gestionar la cola de tareas.

-   **Base de Datos**: [**SQLAlchemy**](https://www.sqlalchemy.org/)
    -   Actúa como el ORM (Object-Relational Mapper) para interactuar con la base de datos.
    -   Por defecto, utiliza **SQLite** para facilitar el desarrollo, pero está configurado para conectarse a una base de datos **PostgreSQL** en un entorno de producción (ver el archivo `.env` en la raíz del proyecto).
    -   Los modelos de datos se definen en `backend/app/models/`.

-   **Comunicación en Tiempo Real**: **WebSockets**
    -   FastAPI gestiona conexiones WebSocket para enviar actualizaciones sobre el progreso de las tareas de exportación desde el backend hacia el frontend. Esto permite que la interfaz de usuario muestre el estado de un trabajo en tiempo real sin necesidad de recargar la página.

## Estructura de Directorios

El proyecto está organizado de la siguiente manera:

```
backend/
└── app/
    ├── __init__.py
    ├── api/                 # Módulos de la API (Endpoints)
    ├── core/                # Lógica de negocio y servicios principales
    ├── db/                  # Configuración de la base de datos y sesión
    ├── models/              # Modelos de datos de SQLAlchemy
    ├── schemas/             # Esquemas de Pydantic para validación
    ├── tasks/               # Tareas asíncronas de Celery
    └── main.py              # Punto de entrada de la aplicación FastAPI
```

## Configuración

Toda la configuración del backend se gestiona a través de variables de entorno definidas en el archivo `.env` ubicado en la raíz del proyecto. Esto incluye:

-   Credenciales de la base de datos (PostgreSQL o SQLite).
-   Credenciales de la API de DocuWare.
-   Configuración del broker de Celery (Redis).

**Nota**: Este componente no se ejecuta de forma independiente, sino como parte del `docker-compose.yml` general del proyecto. Para instrucciones sobre cómo levantar todo el entorno, por favor, consulte el `README.md` en la raíz del repositorio.
