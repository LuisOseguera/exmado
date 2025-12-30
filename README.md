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
- Frontend: React, TypeScript, Material-UI _(próximamente)_
- Base de datos: SQLite (desarrollo) / PostgreSQL (producción)
- Cola de tareas: Redis + Celery

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.10+
- Docker (para Redis)
- Acceso a DocuWare API

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/LuisOseguera/exmado.git
cd exmado/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de DocuWare

# Iniciar Redis
docker-compose up -d

# Iniciar servidor
python app/main.py
```

Acceder a: http://localhost:8000

**Documentación interactiva:** http://localhost:8000/docs

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
├── backend/           # API REST y lógica de negocio
│   ├── app/
│   │   ├── models/    # Modelos de base de datos
│   │   ├── schemas/   # Validación de datos
│   │   ├── api/       # Endpoints REST
│   │   ├── services/  # Lógica de negocio
│   │   └── tasks/     # Tareas asíncronas
│   └── tests/
├── frontend/          # Aplicación React (próximamente)
└── docs/             # Documentación
```

### Contribuir

Este es un proyecto interno. Para sugerencias o reportar problemas:

1. Crear un issue en GitHub
2. Contactar al equipo de desarrollo
3. Enviar pull request (previa coordinación)

## 📊 Estado del Proyecto

**Fase Actual:** Desarrollo del Backend (Fase 1)

- [x] Modelos de base de datos
- [x] Configuración y estructura base
- [x] Sistema de schemas de validación
- [ ] Servicios de negocio
- [ ] Endpoints de API
- [ ] Tareas de Celery
- [ ] Tests unitarios
- [ ] Frontend (Fase 2)

## ⚠️ Notas de Seguridad

- **NUNCA** subir archivos `.env` con credenciales reales
- Las credenciales de DocuWare deben manejarse exclusivamente via variables de entorno
- Para producción, usar secretos gestionados (AWS Secrets Manager, Azure Key Vault, etc.)

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
