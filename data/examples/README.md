# Ejemplos de uso de DocN8NAgent

Este directorio contiene ejemplos de documentos y código para demostrar las capacidades del sistema.

## Documentos de Ejemplo

### 1. Cédula de Ciudadanía
- `cedula_ejemplo.pdf` - Cédula de ciudadanía colombiana
- Campos extraídos: número, nombres, apellidos, fecha de nacimiento, lugar de expedición

### 2. Estado de Cuenta
- `estado_cuenta_ejemplo.pdf` - Estado de cuenta bancario
- Campos extraídos: número de cuenta, titular, saldo, fecha de corte, movimientos

### 3. Carta Laboral
- `carta_laboral_ejemplo.pdf` - Certificación laboral
- Campos extraídos: empleado, empresa, cargo, salario, fecha de ingreso

### 4. RUT
- `rut_ejemplo.pdf` - Registro Único Tributario
- Campos extraídos: NIT, razón social, actividad económica, régimen tributario

## Scripts de Ejemplo

### 1. Procesamiento Básico
```python
# ejemplo_basico.py
import asyncio
from src.agents.document_agent import DocumentProcessingAgent
from src.models.schemas import Document

async def procesar_documento():
    agent = DocumentProcessingAgent()
    
    document = Document(
        id="ejemplo_1",
        filename="cedula.pdf",
        file_path="data/examples/cedula_ejemplo.pdf",
        file_size=1024,
        mime_type="application/pdf"
    )
    
    result = await agent.process_document(document)
    print(f"Tipo detectado: {result.classification.document_type}")
    print(f"Datos extraídos: {result.extraction.fields}")

if __name__ == "__main__":
    asyncio.run(procesar_documento())
```

### 2. Uso de la API
```python
# ejemplo_api.py
import requests

# Subir documento
with open("documento.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/upload",
        files={"file": f}
    )
    document_id = response.json()["document_id"]

# Procesar documento
response = requests.post(f"http://localhost:8000/process/{document_id}")

# Obtener resultado
response = requests.get(f"http://localhost:8000/result/{document_id}")
result = response.json()
```

### 3. Análisis por Lotes
```python
# ejemplo_lotes.py
import asyncio
import os
from pathlib import Path
from src.agents.document_agent import DocumentProcessingAgent

async def procesar_lote(directorio):
    agent = DocumentProcessingAgent()
    resultados = []
    
    for archivo in Path(directorio).glob("*.pdf"):
        document = Document(
            id=str(archivo.stem),
            filename=archivo.name,
            file_path=str(archivo),
            file_size=archivo.stat().st_size,
            mime_type="application/pdf"
        )
        
        result = await agent.process_document(document)
        resultados.append(result)
    
    return resultados
```

## Configuraciones de Ejemplo

### 1. Configuración Personalizada
```python
# config_personalizada.py
from src.core.config import DOCUMENT_CONFIG

# Personalizar configuración
DOCUMENT_CONFIG["ocr_language"] = "spa+eng"  # Español e inglés
DOCUMENT_CONFIG["classification_threshold"] = 0.8
DOCUMENT_CONFIG["extraction_confidence"] = 0.7
```

### 2. Entrenamiento de Modelo
```python
# entrenar_modelo.py
from src.services.classification_service import DocumentClassifier

# Datos de entrenamiento
training_data = [
    {"text": "CÉDULA DE CIUDADANÍA...", "document_type": "cedula"},
    {"text": "ESTADO DE CUENTA...", "document_type": "estado_cuenta"},
    # ... más datos
]

classifier = DocumentClassifier()
classifier.train_ml_model(training_data)
```

## Casos de Uso Avanzados

### 1. Validación Personalizada
Implementar reglas de validación específicas para tu organización.

### 2. Detección de Fraudes
Configurar patrones específicos de detección de documentos fraudulentos.

### 3. Integración con Sistemas Existentes
Conectar con bases de datos y sistemas de la organización.

### 4. Procesamiento en Tiempo Real
Implementar procesamiento automático de documentos subidos.

## Métricas y Monitoreo

El sistema incluye métricas para:
- Tiempo de procesamiento
- Precisión de clasificación
- Confianza en extracción
- Tasa de detección de fraudes
- Errores y excepciones
