# Configuración de Docker para DocN8NAgent
FROM python:3.11-slim

# Metadatos
LABEL maintainer="DocN8NAgent Team"
LABEL description="Agente de IA para procesamiento de documentos bancarios"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalar modelos de spaCy
RUN python -m spacy download es_core_news_sm && \
    python -m spacy download en_core_web_sm

# Copiar código fuente
COPY src/ ./src/
COPY demo.py .
COPY install_deps.py .

# Crear directorios necesarios
RUN mkdir -p data/uploads data/examples data/processed \
             models/trained logs config

# Crear usuario no root
RUN useradd --create-home --shell /bin/bash docn8n
RUN chown -R docn8n:docn8n /app
USER docn8n

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["python", "-m", "src.api.main"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
