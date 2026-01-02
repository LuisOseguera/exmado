#!/bin/bash

# Script para iniciar el worker de Celery
# Uso: bash start_worker.sh

echo "=========================================="
echo "ÉXMADO - Iniciando Celery Worker"
echo "=========================================="
echo ""

# Verificar que estamos en el directorio backend
if [ ! -f "app/celery_app.py" ]; then
    echo "❌ Error: Este script debe ejecutarse desde el directorio backend/"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "✓ Activando entorno virtual..."
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Verificar que Redis esté corriendo
echo "✓ Verificando Redis..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis no está corriendo."
    echo "   Iniciar con: docker-compose up -d"
    echo "   O instalar Redis localmente"
    exit 1
fi

echo "✓ Redis está corriendo"
echo ""
echo "Iniciando worker..."
echo "Presiona Ctrl+C para detener"
echo ""

# Iniciar worker
celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --pool=solo
