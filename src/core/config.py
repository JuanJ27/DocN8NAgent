"""
Configuración principal del sistema DocN8NAgent
"""
import os
from pathlib import Path
from typing import Dict, Any

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Crear directorios si no existen
for dir_path in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(exist_ok=True)

# Configuración de procesamiento de documentos
DOCUMENT_CONFIG = {
    "supported_formats": [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".docx"],
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "ocr_language": "spa",  # Español
    "classification_threshold": 0.7,
    "extraction_confidence": 0.8
}

# Configuración de modelos
MODEL_CONFIG = {
    "document_classifier": "microsoft/DialoGPT-medium",
    "text_extractor": "distilbert-base-multilingual-cased", 
    "fraud_detector": "scikit-learn",
    "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
}

# Configuración de API
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": True,
    "log_level": "info"
}

# Configuración de logging
LOG_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
    "rotation": "1 day",
    "retention": "30 days"
}

# Tipos de documentos bancarios soportados
DOCUMENT_TYPES = {
    "cedula": "Cédula de Ciudadanía",
    "pasaporte": "Pasaporte",
    "licencia": "Licencia de Conducir", 
    "rut": "RUT",
    "estado_cuenta": "Estado de Cuenta",
    "carta_laboral": "Carta Laboral",
    "declaracion_renta": "Declaración de Renta",
    "solicitud_credito": "Solicitud de Crédito",
    "contrato": "Contrato",
    "pagare": "Pagaré"
}

# Campos a extraer por tipo de documento
EXTRACTION_FIELDS = {
    "cedula": ["numero_documento", "nombres", "apellidos", "fecha_nacimiento", "lugar_expedicion"],
    "estado_cuenta": ["numero_cuenta", "titular", "saldo", "fecha_corte", "movimientos"],
    "carta_laboral": ["empleado", "empresa", "cargo", "salario", "fecha_ingreso"],
    "solicitud_credito": ["solicitante", "monto", "plazo", "destino", "ingresos"]
}
