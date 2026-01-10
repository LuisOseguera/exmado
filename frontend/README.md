# Frontend Éxmado

## Descripción General

Este directorio contiene el código fuente de la interfaz de usuario para el proyecto Éxmado. Es una aplicación de página única (SPA) desarrollada con **React** y **TypeScript**, diseñada para ofrecer una experiencia de usuario fluida e interactiva para la gestión de tareas de exportación de documentos.

## Arquitectura y Tecnologías

El frontend está construido sobre un stack moderno de tecnologías web, enfocado en la eficiencia del desarrollo y el rendimiento.

-   **Librería de UI**: [**React**](https://react.dev/)
    -   Se utiliza para construir la interfaz de usuario a través de una arquitectura basada en componentes reutilizables.
    -   Emplea **Hooks** para la gestión del estado y el ciclo de vida de los componentes.

-   **Lenguaje**: [**TypeScript**](https://www.typescriptlang.org/)
    -   Añade un sistema de tipado estático a JavaScript, lo que mejora la robustez del código, facilita el mantenimiento y previene errores comunes durante el desarrollo.

-   **Herramienta de Construcción**: [**Vite**](https://vitejs.dev/)
    -   Proporciona un entorno de desarrollo extremadamente rápido con Hot Module Replacement (HMR) y optimiza el proceso de empaquetado para producción.

-   **Gestión de Estado del Servidor**: [**React Query (TanStack Query)**](https://tanstack.com/query/latest)
    -   Simplifica la obtención, el almacenamiento en caché, la sincronización y la actualización del estado del servidor en la aplicación. Gestiona automáticamente las recargas en segundo plano y el estado de carga/error.

-   **Componentes de UI**: [**Material-UI (MUI)**](https://mui.com/)
    -   Ofrece un conjunto completo de componentes de UI personalizables y listos para usar, permitiendo construir interfaces de usuario elegantes y consistentes de manera rápida.

-   **Cliente HTTP**: [**Axios**](https://axios-http.com/)
    -   Se utiliza para realizar peticiones a la API del backend de forma sencilla y eficiente.

## Estructura de Directorios

La estructura del proyecto está organizada para separar las responsabilidades y facilitar la navegación:

```
frontend/
└── src/
    ├── api/                 # Configuración de Axios y llamadas a la API
    ├── assets/              # Imágenes, fuentes y otros archivos estáticos
    ├── components/          # Componentes de React reutilizables
    ├── hooks/               # Hooks personalizados (ej. useJobProgress para WebSockets)
    ├── types/               # Definiciones de tipos y interfaces de TypeScript
    ├── App.tsx              # Componente principal de la aplicación
    └── main.tsx             # Punto de entrada de la aplicación
```

## Comunicación con el Backend

-   **API REST**: La aplicación realiza peticiones HTTP a la API del backend (FastAPI) para crear y consultar trabajos de exportación. La configuración del proxy en `vite.config.ts` redirige las llamadas `/api` al backend durante el desarrollo para evitar problemas de CORS.
-   **WebSockets**: Se establece una conexión WebSocket con el backend para recibir actualizaciones en tiempo real sobre el progreso de los trabajos. El hook `useJobProgress` encapsula esta lógica, permitiendo que los componentes se suscriban fácilmente a las actualizaciones de un trabajo específico.

**Nota**: Este componente no se ejecuta de forma independiente. Para levantar todo el entorno de desarrollo, incluyendo el frontend, backend y los servicios asociados, por favor, siga las instrucciones detalladas en el `README.md` ubicado en la raíz del repositorio del proyecto.
