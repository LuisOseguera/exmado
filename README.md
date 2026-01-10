# Éxmado

**Éxmado** (_Extracción Masiva de Documentos_) es un sistema de autoservicio diseñado para que vos podás realizar descargas masivas de documentos desde DocuWare de forma sencilla y autónoma.

## 🎯 ¿Qué Problema Resolvemos?

En lugar de solicitar scripts personalizados cada vez que necesitás una descarga masiva, Éxmado te da una interfaz web para que vos mismo configurés y ejecutés los trabajos de extracción, monitoreando el progreso en tiempo real.

### Características Principales

- **Autoservicio:** Creá y gestioná tus propias descargas sin depender de IT.
- **Configuración Flexible:** Mapeá dinámicamente las columnas de tu Excel con los campos de DocuWare.
- **Procesamiento Asíncrono:** La aplicación trabaja en segundo plano para descargar miles de documentos sin bloquear tu computadora.
- **Monitoreo en Tiempo Real:** Mirá el progreso de tus trabajos de descarga al instante.
- **Historial Completo:** Llevá un registro de todas las extracciones que has realizado.

---

## 🚀 Cómo Poner a Correr el Proyecto

Gracias a Docker, levantar todo el entorno de desarrollo es súper sencillo. Solo necesitás tener **Docker** y **Docker Compose** instalados en tu máquina.

**¡Y listo! Con un solo comando, tenés todo funcionando:**

```bash
docker-compose up --build
```

Este comando hará lo siguiente:
1.  **Construirá las imágenes** de Docker para el frontend y el backend.
2.  **Levantará todos los servicios** en contenedores separados:
    -   `frontend`: La aplicación web de React.
    -   `backend`: La API de FastAPI.
    -   `celery_worker`: El trabajador que procesa las descargas.
    -   `redis`: El sistema que gestiona la cola de tareas.
    -   `nginx`: El servidor que dirige el tráfico a los servicios correctos.
3.  Una vez que todo esté corriendo, podés acceder a la aplicación en tu navegador en la siguiente dirección: **[http://localhost:8080](http://localhost:8080)**

---

## 🏗️ Arquitectura del Sistema

El proyecto está completamente "containerizado" usando Docker, lo que asegura que funcione de la misma manera en cualquier máquina.

```
                  ┌────────────────┐
                  │   Tu Navegador │
                  └───────┬────────┘
                          │ (localhost:8080)
                  ┌───────▼────────┐
                  │     Nginx      │ (Proxy Inverso)
                  └───────┬────────┘
          ┌───────────────┴───────────────┐
          │ (peticiones /api)             │ (otras peticiones)
┌─────────▼─────────┐             ┌───────▼─────────┐
│     Backend       │             │     Frontend    │
│    (FastAPI)      │             │     (React)     │
└─────────┬─────────┘             └─────────────────┘
          │ (tareas)
┌─────────▼─────────┐             ┌────────────────┐
│  Celery Worker(s) │◀───────────▶│      Redis     │
└─────────┬─────────┘             │ (Cola de Tareas)│
          │                       └────────────────┘
┌─────────▼─────────┐
│  API de DocuWare  │
└───────────────────┘
```

### Stack Tecnológico

- **Backend:** Python, FastAPI, Celery, SQLAlchemy.
- **Frontend:** React, TypeScript, Material-UI, TanStack Query.
- **Infraestructura:** Docker, Docker Compose, Nginx.
- **Base de Datos:** SQLite (para desarrollo, dentro del contenedor del backend).
- **Cola de Tareas:** Redis.

---

## 🔧 Desarrollo y Estructura

El código está organizado en dos carpetas principales:

```
exmado/
├── backend/     # Contiene toda la lógica de la API y los trabajadores de Celery.
├── frontend/    # Contiene toda la aplicación web construida en React.
├── nginx.conf   # Configuración del proxy inverso Nginx.
└── docker-compose.yml # El archivo que orquesta todos los servicios.
```

### Notas Importantes para el Desarrollo

- **Variables de Entorno:** Las credenciales y configuraciones sensibles (como las de DocuWare) se deben gestionar a través de un archivo `.env` dentro de la carpeta `backend/`. **Nunca subás este archivo a Git.**
- **Volúmenes de Docker:** El `docker-compose.yml` está configurado para montar tu código local directamente en los contenedores (`./frontend:/app` y `./backend:/app`). Esto significa que cualquier cambio que guardés en tu código se reflejará automáticamente en la aplicación en ejecución, sin necesidad de reconstruir la imagen. Simplemente guardá y el servidor de desarrollo se recargará solo.

## 💡 Próximos Pasos

- **Solucionar el Problema del WebSocket:** Diagnosticar y corregir el error que impide la comunicación en tiempo real para el progreso de los trabajos.
- **Migrar a PostgreSQL:** Cambiar la base de datos de SQLite a PostgreSQL para un entorno de producción más robusto.
- **Autenticación de Usuarios:** Implementar un sistema de inicio de sesión para controlar el acceso.
- **Expandir Cobertura de Pruebas:** Añadir más pruebas unitarias y de integración.
