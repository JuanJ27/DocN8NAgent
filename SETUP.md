# DocN8NAgent - Setup del Proyecto

Este script configura el entorno de desarrollo para DocN8NAgent.

## Instalación

### 1. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Instalar modelos adicionales

#### spaCy (para NLP en español)
```bash
python -m spacy download es_core_news_sm
```

#### Tesseract OCR
**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-spa
```

**CentOS/RHEL:**
```bash
sudo yum install tesseract tesseract-langpack-spa
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki

### 4. Configurar herramientas de desarrollo
```bash
pre-commit install
```

## Estructura del Proyecto

```
DocN8NAgent/
├── src/
│   ├── agents/           # Agentes de IA
│   ├── api/             # API REST
│   ├── core/            # Configuración y utilidades
│   ├── models/          # Modelos de datos
│   ├── services/        # Servicios de procesamiento
│   └── utils/           # Utilidades
├── tests/               # Tests unitarios
├── data/                # Datos de ejemplo
├── models/              # Modelos entrenados
├── logs/                # Logs del sistema
├── docs/                # Documentación
└── config/              # Configuraciones
```

## Uso Rápido

### 1. Iniciar el servidor API
```bash
python -m src.api.main
```

### 2. Usar el cliente CLI
```bash
# Verificar estado
python -m src.cli status

# Procesar documento
python -m src.cli process path/to/document.pdf

# Ver lista de documentos
python -m src.cli list

# Ver estadísticas
python -m src.cli stats
```

### 3. Usar la API directamente
```bash
# Subir documento
curl -X POST "http://localhost:8000/upload" -F "file=@documento.pdf"

# Procesar documento
curl -X POST "http://localhost:8000/process/{document_id}"

# Ver resultado
curl "http://localhost:8000/result/{document_id}"
```

## Datos de Prueba

Coloca documentos de ejemplo en la carpeta `data/examples/`:
- Cédulas de ciudadanía
- Estados de cuenta
- Cartas laborales
- RUTs
- Solicitudes de crédito

## Desarrollo

### Ejecutar tests
```bash
pytest tests/ -v
```

### Formatear código
```bash
black src/ tests/
```

### Linting
```bash
flake8 src/ tests/
```

## Producción

Para producción, considera:

1. **Base de datos**: Reemplazar almacenamiento en memoria por PostgreSQL/MongoDB
2. **Cola de tareas**: Usar Celery con Redis/RabbitMQ
3. **Almacenamiento**: AWS S3 o similar para archivos
4. **Monitoreo**: Prometheus + Grafana
5. **Logs**: ELK Stack o similar
6. **Seguridad**: HTTPS, autenticación JWT, rate limiting

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **PyTorch/Transformers**: Modelos de IA y NLP
- **Tesseract + EasyOCR**: Reconocimiento óptico de caracteres
- **spaCy**: Procesamiento de lenguaje natural
- **OpenCV**: Procesamiento de imágenes
- **scikit-learn**: Algoritmos de machine learning
- **Rich**: Interface CLI atractiva
- **Pytest**: Framework de testing
