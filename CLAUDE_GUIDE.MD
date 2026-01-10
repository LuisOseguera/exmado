# Guía de Traspaso para Claude

¡Hola, Claude! Soy Jules, el agente de IA que trabajó en este proyecto antes que vos. Te he preparado esta guía para que tengás un traspaso lo más fluido posible.

## 1. Resumen del Proyecto

**Éxmado** es una aplicación web diseñada para automatizar la descarga masiva de documentos desde un sistema DocuWare. El usuario puede subir un archivo de Excel con los criterios de búsqueda y la aplicación procesa la exportación en segundo plano, mostrando el progreso en tiempo real.

La arquitectura es la siguiente:
*   **Frontend**: React + TypeScript con Vite, Material-UI y React Query.
*   **Backend**: FastAPI (Python) con Celery para tareas asíncronas.
*   **Base de Datos**: SQLite por defecto, configurable a PostgreSQL.
*   **Broker de Mensajes**: Redis (para Celery).
*   **Servidor Web**: Nginx como proxy inverso.
*   **Orquestación**: Todo el stack está contenedorizado y se gestiona con un único archivo `docker-compose.yml` en la raíz.

## 2. Estado Actual

El proyecto se encuentra en un estado de **código limpio, documentado y funcional**. Mi misión principal fue solucionar un error persistente de conexión de WebSockets, además de refactorizar y profesionalizar toda la base de código.

## 3. Cambios Realizados

Aquí te resumo las tareas más importantes que completé:

1.  **Solución del Problema de WebSocket**: El error principal (`WebSocket is closed before the connection is established`) fue solucionado implementando Nginx como un proxy inverso. Nginx ahora gestiona todo el tráfico, dirigiendo las peticiones `/api` y `/ws` al backend, y el resto al frontend.
2.  **Contenerización Completa**: Unifiqué todo el proyecto (frontend, backend, worker, redis, nginx) bajo un solo `docker-compose.yml` en la raíz. Ahora, todo el entorno se levanta con un único comando.
3.  **Limpieza y Refactorización del Código**:
    *   Eliminé todo el código no utilizado y los componentes de prueba.
    *   Reescribí los comentarios en todo el código fuente (frontend y backend) para que sean profesionales, claros y estén en español de Honduras (voseo).
    *   Eliminé comentarios informales, emojis y cualquier elemento no profesional.
4.  **Actualización de la Documentación**:
    *   Reescribí por completo los `README.md` de la raíz, del `frontend/` y del `backend/` para que reflejen la nueva estructura simplificada y el proceso de inicio con Docker.

## 4. Detalles de la Solución del WebSocket

El problema original se debía a una incorrecta configuración de la red entre los contenedores y el navegador. La solución fue utilizar Nginx para unificar el punto de entrada. La URL de conexión del WebSocket en el frontend (`frontend/src/hooks/useJobProgress.ts`) se configuró así:

```typescript
const wsUrl = `ws://${window.location.host}/ws/jobs/${jobId}`;
```

`window.location.host` se asegura de que el frontend siempre intente conectar al mismo host desde el que se sirve la página (en este caso, el contenedor de Nginx en el puerto `8080`), y Nginx se encarga de redirigir la petición `/ws/...` al backend de FastAPI.

## 5. Instrucciones y Próximos Pasos

Tu misión es familiarizarte con el código y continuar con el desarrollo de nuevas funcionalidades según lo requiera el usuario.

1.  **Cómo Iniciar el Entorno**:
    *   Navegá a la raíz del proyecto.
    *   Ejecutá el comando: `docker-compose up --build`. Esto levantará todos los servicios.

2.  **Cómo Verificar la Aplicación**:
    *   Abrí la aplicación en tu navegador: `http://localhost:8080`.
    *   La aplicación debería cargar y ser completamente funcional. Podés crear un nuevo trabajo de exportación y ver el progreso en tiempo real para confirmar que la conexión WebSocket funciona correctamente.

¡Mucha suerte! El código base ahora está estable, limpio y bien documentado, lo que debería darte un excelente punto de partida.
