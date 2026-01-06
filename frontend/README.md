# Éxmado Frontend

Aplicación web React + TypeScript para el sistema de descarga masiva de documentos.

## 🚀 Instalación y Ejecución

### Requisitos

- Node.js (versión 18 o superior)
- npm (generalmente se instala con Node.js)

### 1. Navegar al Directorio

Desde la raíz del proyecto, entra a la carpeta del frontend.
```bash
cd frontend
```

### 2. Instalar Dependencias

Instala todas las librerías necesarias para el proyecto.
```bash
npm install
```

### 3. Iniciar el Servidor de Desarrollo

Ejecuta el siguiente comando para arrancar la aplicación en modo de desarrollo.
```bash
npm run dev
```
La aplicación estará disponible en `http://localhost:5173` y se recargará automáticamente al guardar cambios.

### Producción

```bash
npm run build
npm run preview
```

## 📁 Estructura

```
frontend/
├── public/               # Archivos estáticos
├── src/
│   ├── components/       # Componentes React
│   │   ├── JobsList.tsx
│   │   └── Stubs.tsx     # Componentes temporales
│   ├── pages/
│   │   └── Dashboard.tsx # Página principal
│   ├── services/
│   │   └── api.ts        # Cliente API
│   ├── hooks/
│   │   └── useJobProgress.ts  # WebSocket hook
│   ├── types/
│   │   └── index.ts      # TypeScript types
│   ├── App.tsx           # App principal
│   └── main.tsx          # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## 🎯 Estado del Proyecto

El frontend está en una fase de desarrollo activa. La estructura base, la comunicación con el backend y las vistas principales están implementadas.

- **Completado:**
    - Estructura del proyecto con Vite, React y TypeScript.
    - Conexión con la API REST del backend mediante Axios y React Query.
    - Integración con WebSockets para recibir actualizaciones en tiempo real.
    - Dashboard principal que lista las tareas de descarga.
- **En Desarrollo:**
    - Vista de detalles de una tarea (`JobDetails`).
    - Asistente de creación de nuevas tareas (`CreateJobWizard`).
    - Mejoras en la gestión de errores y notificaciones al usuario.

## 🔧 Tecnologías

- **React 18** - UI framework
- **TypeScript** - Tipado estático
- **Vite** - Build tool
- **Material-UI (MUI)** - Componentes UI
- **React Query** - Server state management
- **Axios** - HTTP client
- **React Router** - Navegación
- **date-fns** - Manejo de fechas

## 🌐 Conexión con el Backend

El frontend está diseñado para comunicarse con el backend de Éxmado, que debe estar corriendo en `http://localhost:8000`.

- **API REST**: Las peticiones a `/api/...` son redirigidas automáticamente al backend gracias al proxy configurado en `vite.config.ts`. Esto evita problemas de CORS durante el desarrollo.
- **WebSockets**: Se conecta al endpoint `ws://localhost:8000/ws` para recibir actualizaciones en tiempo real sobre el progreso de las descargas.

## 📊 Flujo de la Aplicación

```
1. Dashboard
   ├─► Lista de Jobs Activos
   │   └─► JobDetails (con progreso en tiempo real)
   │
   ├─► Lista de Jobs Históricos
   │   └─► JobDetails (con logs y estadísticas)
   │
   └─► Botón "Nuevo Job"
       └─► CreateJobWizard
           ├─► Step 1: Upload Excel
           ├─► Step 2: Seleccionar Cabinet/Dialog
           ├─► Step 3: Mapear Campos
           ├─► Step 4: Configurar Transformaciones
           └─► Step 5: Ejecutar (modo prueba o completo)
```

## 🎨 Temas y Estilos

El tema se configura en `App.tsx`:

- Paleta de colores personalizable
- Modo claro (dark mode pendiente)
- Responsive design

## 🔌 WebSocket

El hook `useJobProgress` se conecta automáticamente al WebSocket del backend:

```typescript
const { progress, isConnected } = useJobProgress(jobId);

// progress contiene:
// - type: 'progress' | 'completed' | 'error'
// - processed_records
// - total_records
// - progress_percentage
// - latest_log
```

## 📝 Próximos Pasos

### Componentes Pendientes

1. **JobDetails Completo**

   - Progreso en tiempo real con barra animada
   - Lista de records procesados
   - Logs en tiempo real
   - Botones de control (pausar, cancelar, reiniciar)

2. **CreateJobWizard**

   - Step 1: Drag & drop Excel con preview
   - Step 2: Selector de Cabinet/Dialog
   - Step 3: Mapeo visual columnas → campos
   - Step 4: Configuración de transformaciones
   - Step 5: Preview y ejecución

3. **Extras**
   - Notificaciones con Snackbar
   - Dark mode
   - Exportar reportes
   - Filtros avanzados

## 🐛 Debugging

### Problemas Comunes

**Error de CORS:**

- Verificar que el backend esté corriendo
- Verificar proxy en `vite.config.ts`

**WebSocket no conecta:**

- Verificar URL en `useJobProgress`
- Verificar que el endpoint `/ws/jobs/{id}` existe

**Tipos TypeScript:**

- Ejecutar: `npm run build` para verificar tipos
- Actualizar tipos en `src/types/index.ts`

## 📚 Referencias

- [React Documentation](https://react.dev/)
- [Material-UI](https://mui.com/)
- [React Query](https://tanstack.com/query)
- [Vite](https://vitejs.dev/)
