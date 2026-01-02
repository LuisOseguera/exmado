# Éxmado Frontend

Aplicación web React + TypeScript para el sistema de descarga masiva de documentos.

## 🚀 Inicio Rápido

### Instalación

```bash
cd frontend
npm install
```

### Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en: http://localhost:3000

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

## 🎯 Características Implementadas

### ✅ Completado

- ✅ Configuración base (Vite + React + TypeScript)
- ✅ Cliente API con Axios
- ✅ React Query para manejo de estado
- ✅ Material-UI para componentes
- ✅ WebSocket hook para progreso en tiempo real
- ✅ Lista de jobs con auto-refresh
- ✅ Dashboard principal
- ✅ Tipos TypeScript completos

### 🚧 En Desarrollo

- 🚧 JobDetails (detalles completos del job)
- 🚧 CreateJobWizard (wizard de creación)
- 🚧 Componentes de progreso en tiempo real
- 🚧 Gestión de errores mejorada

## 🔧 Tecnologías

- **React 18** - UI framework
- **TypeScript** - Tipado estático
- **Vite** - Build tool
- **Material-UI (MUI)** - Componentes UI
- **React Query** - Server state management
- **Axios** - HTTP client
- **React Router** - Navegación
- **date-fns** - Manejo de fechas

## 🌐 API Backend

El frontend se comunica con el backend en:

- **REST API**: http://localhost:8000/api
- **WebSocket**: ws://localhost:8000/ws

El proxy de Vite redirige automáticamente las peticiones.

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
