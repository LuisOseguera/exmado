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

# Intentar primero con redis-cli (si está instalado)
if command -v redis-cli &>/dev/null; then
	if redis-cli ping >/dev/null 2>&1; then
		echo "✓ Redis está corriendo (verificado con redis-cli)"
	else
		echo "⚠️  redis-cli no puede conectar"
	fi
else
	# Si redis-cli no está disponible, verificar con Docker
	if command -v docker &>/dev/null; then
		if docker ps | grep -q redis; then
			echo "✓ Redis está corriendo en Docker"
		else
			echo "⚠️  Redis no está corriendo en Docker"
			echo "   Iniciar con: docker-compose up -d"
			exit 1
		fi
	else
		echo "⚠️  No se puede verificar Redis (redis-cli y docker no disponibles)"
		echo "   Asegúrate de que Redis esté corriendo antes de continuar"
		echo ""
		read -p "¿Continuar de todas formas? (s/n): " -n 1 -r
		echo
		if [[ ! $REPLY =~ ^[Ss]$ ]]; then
			exit 1
		fi
	fi
fi

echo ""
echo "Iniciando worker..."
echo "Presiona Ctrl+C para detener"
echo ""

# Iniciar worker
# En Windows (Git Bash/MSYS), usar --pool=solo
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
	celery -A app.celery_app worker \
		--loglevel=info \
		--concurrency=2 \
		--pool=solo
else
	celery -A app.celery_app worker \
		--loglevel=info \
		--concurrency=2 \
		--pool=prefork
fi
