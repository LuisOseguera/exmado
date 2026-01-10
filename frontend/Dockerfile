# Usar una imagen base de Node.js
FROM node:18-alpine

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de definición de dependencias
COPY package*.json ./

# Instalar las dependencias del proyecto
RUN npm install

# Copiar el resto de los archivos de la aplicación
COPY . .

# Exponer el puerto que usa Vite
EXPOSE 3000

# Comando para iniciar el servidor de desarrollo y hacerlo accesible externamente
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
