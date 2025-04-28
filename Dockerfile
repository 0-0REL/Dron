FROM python:3.12-slim
LABEL maintainer="Rodrigo Arellano"
LABEL description="Control del dron"
LABEL version="1.0"

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    python3-opencv
RUN rm -rf /var/lib/apt/lists/*
# Set the working directory
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# 3. Copia SOLO el código fuente (src/) al contenedor
COPY ./src/ ./src/

# 4. Define el WORKDIR final (donde se ejecutará el código)
WORKDIR /app/src

# 5. Comando de inicio (ejecuta main.py)
CMD ["python", "main.py"]