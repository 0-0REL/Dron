FROM arm32v7/debian:buster

# Configurar repositorios archivados para Buster
RUN echo "deb http://archive.debian.org/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security/ buster/updates main" >> /etc/apt/sources.list && \
    echo "Acquire::Check-Valid-Until false;" > /etc/apt/apt.conf.d/90ignore-release-date && \
    echo "Acquire::AllowInsecureRepositories true;" >> /etc/apt/apt.conf.d/90ignore-release-date && \
    echo "Acquire::AllowDowngradeToInsecureRepositories true;" >> /etc/apt/apt.conf.d/90ignore-release-date

# Instalar Python 3.7 y dependencias
RUN apt-get update && apt-get install -y \
    libwebp-dev \
    libwebp6 \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libatlas-base-dev \
    libtbb2 \
    libtbb-dev \
    libdc1394-22-dev \
    python3.7 \
    python3-pip \
    python3.7-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    gfortran \
    libhdf5-dev \
    libc-ares-dev \
    libeigen3-dev \
    libatlas-base-dev \
    libopenblas-dev \
    libblas-dev \
    openmpi-bin libopenmpi-dev \
    liblapack-dev \
    cython \
    && rm -rf /var/lib/apt/lists/*

# Crear enlace simbólico para python3 -> python3.7
RUN ln -sf /usr/bin/python3.7 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.7 /usr/bin/python

# Verificar instalación
RUN python --version && \
    python3 --version

# Establecer directorio de trabajo
WORKDIR /app

# Configurar pip para usar piwheels (CRUCIAL)
RUN echo "[global]" > /etc/pip.conf && \
    echo "extra-index-url = https://www.piwheels.org/simple" >> /etc/pip.conf && \
    echo "trusted-host = www.piwheels.org" >> /etc/pip.conf
# Copiar requirements e instalar paquetes Python
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

#RUN python3 -m pip install --no-cache-dir -r tflite-runtime
RUN pip3 install keras_applications==1.0.8 --no-deps
RUN pip3 install keras_preprocessing==1.1.0 --no-deps
RUN pip3 install -U --user six wheel mock
RUN pip3 install pybind11
RUN pip3 install h5py==2.10.0
# upgrade setuptools 40.8.0 -> 52.0.0
RUN pip3 install --upgrade setuptools


#copiar tensor
COPY tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl .
RUN python3 -m pip install tensorflow-2.1.0-cp37-cp37m-linux_armv7l.whl

RUN pip3 install tflite-runtime

# Copiar script principal
COPY prueba.py .
# Copiar directorios requeridos
COPY BlazeFaceDetection/ ./BlazeFaceDetection/
COPY models/ ./models/

# Asegurar permisos y verificar estructura
RUN chmod -R 755 BlazeFaceDetection && \
    ls -la && \
    ls -la BlazeFaceDetection/

# ESTO ES LO CRUCIAL: Establecer PYTHONPATH
ENV PYTHONPATH="/app:${PYTHONPATH}"

# Exponer puertos
EXPOSE 5000 5001

COPY webcamFaceDetection.py .

# Comando para ejecutar la aplicación
CMD ["python3", "prueba.py"]
