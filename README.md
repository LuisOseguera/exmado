# Éxmado

**Éxmado** (_Extracción Masiva de Documentos_) - Sistema de autoservicio para descarga masiva de documentos desde DocuWare.

## 🎯 ¿Qué es Éxmado?

Éxmado es una aplicación web que permite a usuarios no técnicos realizar descargas masivas de documentos desde DocuWare de forma autónoma, sin necesidad de solicitar scripts personalizados cada vez.

### Características Principales

- ✅ **Autoservicio**: Los usuarios pueden configurar y ejecutar sus propias descargas
- ✅ **Configuración Flexible**: Mapeo dinámico de campos entre Excel y DocuWare
- ✅ **Procesamiento Asíncrono**: Descarga miles de documentos en segundo plano
- ✅ **Monitoreo en Tiempo Real**: Seguimiento del progreso con estadísticas detalladas
- ✅ **Transformaciones Automáticas**: Conversión TIF a PDF, renombrado inteligente
- ✅ **Historial Completo**: Registro de todas las descargas realizadas
- ✅ **Modo de Prueba**: Validar configuración antes de descargas masivas

## 📚 Documentación

- [Guía de Usuario](docs/user_guide.md) _(próximamente)_
- [Documentación de API](docs/api.md) _(próximamente)_
- [Guía de Instalación](backend/README.md)

## 🏗️ Arquitectura

```
┌─────────────┐
│   Frontend  │  React + TypeScript
│   (Web UI)  │
└──────┬──────┘
       │ REST API
┌──────▼──────┐
│   Backend   │  FastAPI + Python
│  (API REST) │
└──────┬──────┘
       │
┌──────▼──────┐
│    Celery   │  Procesamiento asíncrono
│   Workers   │
└──────┬──────┘
       │
┌──────▼──────┐
│   DocuWare  │  API de DocuWare
│     API     │
└─────────────┘
```

**Stack Tecnológico:**

- Backend: Python 3.10+, FastAPI, SQLAlchemy, Celery
- Frontend: React, TypeScript, Material-UI
- Base de datos: SQLite (desarrollo) / PostgreSQL (producción)
- Cola de tareas: Redis + Celery

## 🚀 Instalación y Ejecución

Este proyecto se compone de un backend (API REST con Python/FastAPI) y un frontend (aplicación web con React/TypeScript). Para levantarlo completamente, necesitarás seguir las instrucciones de cada parte.

- **Para instrucciones detalladas del Backend, ve a 👉 `backend/README.md`**
- **Para instrucciones detalladas del Frontend, ve a 👉 `frontend/README.md`**

### Resumen Rápido

1.  **Backend**: Instalar dependencias de Python, configurar el archivo `.env`, iniciar Redis con Docker y arrancar el servidor FastAPI y el worker de Celery.
2.  **Frontend**: Instalar dependencias de Node.js y arrancar el servidor de desarrollo de Vite.

## 📖 Casos de Uso

### Caso 1: Auditoría necesita facturas de proveedores

1. Usuario sube Excel con códigos de proveedor y números de orden
2. Configura mapeo: `Columna_Excel → Campo_DocuWare`
3. Define estructura de carpetas: `Año/Proveedor/Documento`
4. Ejecuta prueba con 10 registros
5. Si todo está bien, ejecuta descarga completa (500+ documentos)
6. Monitorea progreso en tiempo real
7. Recibe notificación al terminar

### Caso 2: Descarga masiva para requerimiento fiscal

1. Usuario configura conversión automática TIF → PDF
2. Define patrón de renombrado personalizado
3. Ejecuta descarga de 17,000 documentos
4. Sistema procesa en 2-3 horas
5. Usuario puede pausar/reanudar si necesita

## 🔧 Desarrollo

### Estructura del Proyecto

```
exmado/
├── backend/           # API REST y lógica de negocio (FastAPI)
│   └── ...
├── frontend/          # Aplicación web (React + TypeScript)
│   └── ...
└── docs/              # Documentación general
```

### Contribuir

Este es un proyecto interno. Para sugerencias o reportar problemas:

1. Crear un issue en GitHub
2. Contactar al equipo de desarrollo
3. Enviar pull request (previa coordinación)

## 📊 Estado del Proyecto

**Fase Actual:** Desarrollo activo de Backend y Frontend.

- **Backend (FastAPI):**
    - [x] Lógica de negocio principal implementada.
    - [x] Endpoints de API funcionales.
    - [x] Tareas asíncronas con Celery operativas.
    - [ ] Pendiente: Mejorar cobertura de tests.
- **Frontend (React):**
    - [x] Estructura base y componentes principales listos.
    - [x] Conexión con API y WebSockets funcional.
    - [ ] Pendiente: Desarrollo de vistas de detalle y wizard de creación.

## ⚠️ Notas de Seguridad

- **NUNCA** subir archivos `.env` con credenciales reales
- Las credenciales de DocuWare deben manejarse exclusivamente via variables de entorno
- Para producción, usar secretos gestionados (AWS Secrets Manager, Azure Key Vault, etc.)

## 💡 Implementaciones Futuras

- **Migración de Base de Datos**: Cambiar de SQLite a PostgreSQL para el entorno de producción.
- **Autenticación de Usuarios**: Implementar un sistema de login para gestionar el acceso.
- **Tests Unitarios**: Aumentar la cobertura de tests tanto en el backend como en el frontend.
- **Modo Oscuro**: Añadir un tema oscuro en la interfaz del frontend.

## 📝 Licencia

Uso interno exclusivo. Todos los derechos reservados.

## 👥 Equipo

**Desarrollado por:** Luis Oseguera - Equipo de Aplicaciones
**Organización:** Servicios Compartidos
**Año:** 2025

## 📞 Soporte

Para soporte técnico:

- Email: loseguera@servicioscompartidos.com
- Teams: Canal de IT - Equipo de Aplicaciones

---

**Estado:** 🚧 En desarrollo activo
