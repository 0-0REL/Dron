# Usamos una imagen base con Python y OpenCV preinstalado
FROM python:3.9-slim

# Instalar dependencias del sistema necesarias para OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script principal
COPY prueba.py .

# Crear estructura de directorios
RUN mkdir -p tensor/modelo_exportado complementos/modelos

# Copiar los archivos del modelo (desde las rutas absolutas que me diste)
COPY tensor/modelo_exportado/modelo.tflite ./tensor/modelo_exportado/
COPY complementos/modelos/deploy.prototxt ./complementos/modelos/
COPY complementos/modelos/res10_300x300_ssd_iter_140000_fp16.caffemodel ./complementos/modelos/

# Comando para ejecutar la aplicación
CMD ["python", "prueba.py"]
EXPOSE 5000 5001
