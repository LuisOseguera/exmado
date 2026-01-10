# Usar una imagen base de Python
FROM python:3.10-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar poetry
RUN pip install poetry

# Copiar el archivo de definición de dependencias
COPY pyproject.toml /app/

# Instalar dependencias (Poetry creará poetry.lock si no existe)
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Copiar el resto de los archivos de la aplicación
COPY . /app/

# Exponer el puerto que usa FastAPI
EXPOSE 8000
