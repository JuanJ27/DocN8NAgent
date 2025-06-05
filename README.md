# DocN8NAgent 🤖📄
*Sistema de Agentes de IA para Procesamiento Documental Bancario*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**DocN8NAgent** es un sistema avanzado de procesamiento documental que utiliza inteligencia artificial para automatizar la gestión de documentos en el sector bancario. El sistema está optimizado para ejecutarse en **sistemas sin GPU**, utilizando únicamente CPU para máxima compatibilidad.

## 🎯 Características Principales

- **🔍 OCR Múltiple**: Tesseract + EasyOCR para máxima precisión
- **📋 Clasificación Inteligente**: Identifica automáticamente tipos de documentos
- **📊 Extracción de Datos**: NLP avanzado para extraer información clave  
- **✅ Validación Automática**: Verifica integridad y detecta posibles fraudes
- **🌐 API REST**: Integración fácil con sistemas existentes
- **💻 CLI Amigable**: Interfaz de línea de comandos para uso directo
- **⚡ Optimizado para CPU**: Funciona sin necesidad de GPU dedicada

## 🚀 Inicio Rápido (CPU Optimizado)

### Pre-requisitos
- Python 3.8+ 
- Sistema Linux/macOS/Windows
- 4GB RAM mínimo (8GB recomendado)

### Instalación Automática
```bash
# Clonar repositorio
git clone <repository-url>
cd DocN8NAgent

# Ejecutar instalación automática para CPU
python install_deps_cpu.py

# O usar script de inicio rápido
./quick_start.sh demo
```

### Instalación Manual
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o venv\Scripts\activate en Windows

# Instalar dependencias CPU-optimizadas
pip install -r requirements.txt

# Instalar dependencias del sistema (Linux)
sudo apt-get install tesseract-ocr tesseract-ocr-spa poppler-utils

# Descargar modelo de spaCy
python -m spacy download es_core_news_sm
```

## 📖 Uso

### 1. Demostración Rápida
```bash
python demo.py
```

### 2. Servidor API
```bash
python -m src.api.main
# Servidor en: http://localhost:8000
# Documentación: http://localhost:8000/docs
```

### 3. CLI Simple
```bash
# Verificar estado
python -m src.cli_simple status

# Procesar documento
python -m src.cli_simple process documento.pdf

# Ver historial
python -m src.cli_simple history
```

### 4. Script de Inicio Rápido
```bash
./quick_start.sh demo    # Ejecutar demostración
./quick_start.sh api     # Iniciar servidor API  
./quick_start.sh cli     # Usar CLI
```
- **Beneficio**: Facilita la organización y el acceso en sistemas digitales.

### 2. Extracción de Datos
- **Descripción**: Uso de OCR (*Optical Character Recognition*) y NLP (*Natural Language Processing*) para extraer datos clave (nombres, fechas, montos) de documentos no estructurados.
- **Beneficio**: Reduce errores humanos y agiliza la integración con sistemas bancarios.

### 3. Validación y Verificación
- **Descripción**: Comparación automática de documentos con bases de datos para asegurar cumplimiento y autenticidad.
- **Beneficio**: Acelera procesos como la aprobación de préstamos.

### 4. Detección de Fraudes
- **Descripción**: Análisis de patrones para identificar actividades sospechosas.
- **Beneficio**: Mejora la seguridad y reduce pérdidas financieras.

### 5. Automatización de Flujos de Trabajo
- **Descripción**: RPA (*Robotic Process Automation*) enruta documentos y gestiona procesos.
- **Beneficio**: Disminuye tiempos operativos.

### 6. Interacción con Clientes
- **Descripción**: Chatbots como Tabot (desarrollado por Bancolombia) resuelven consultas relacionadas con documentos.
- **Beneficio**: Mejora la experiencia del cliente.

---

## Tecnologías Clave

Las siguientes tecnologías son fundamentales para la implementación:

- **OCR**: Convierte imágenes en texto legible por máquinas.
- **Aprendizaje Automático**: Entrena modelos para clasificar y analizar datos.
- **NLP**: Procesa y entiende contenido textual en documentos.
- **Modelos de Lenguaje Grande (LLMs)**: Generan respuestas o resúmenes basados en documentos.
- **RPA**: Automatiza tareas operativas repetitivas.

---

## Beneficios Demostrados

Casos de estudio en el sector financiero destacan los impactos de la IA en el BPO documental:

| **Caso de Estudio**                          | **Impacto**                                     |
|----------------------------------------------|------------------------------------------------|
| Banco líder en procesamiento de préstamos    | 70% menos tiempo (aprobación en 48 horas)      |
| Proveedor de seguros (detección de fraudes)  | $65M menos en pérdidas, falsos positivos de 30% a 5% |
| Banco global (cumplimiento normativo)        | 80% menos tiempo, 75% menos errores manuales   |

Estos resultados sugieren que Bancolombia podría lograr mejoras similares en eficiencia y seguridad.

---

## Desafíos y Consideraciones

La implementación de agentes de IA enfrenta retos que deben abordarse:

1. **Integración con Sistemas Existentes**
   - Requerimiento: Conexión mediante APIs y compatibilidad con infraestructura actual.
   - Solución: Diseñar pipelines de datos robustos.

2. **Entrenamiento Continuo**
   - Requerimiento: Actualización de modelos para nuevos formatos y normativas.
   - Solución: Inversión en datos etiquetados y monitoreo.

3. **Privacidad y Seguridad**
   - Requerimiento: Cumplir con regulaciones de protección de datos.
   - Solución: Encriptación y auditorías regulares.

4. **Costos Iniciales**
   - Requerimiento: Infraestructura computacional y almacenamiento.
   - Solución: Uso de plataformas en la nube (AWS, Azure).

---

## Estrategia Propuesta

1. **Fase Piloto**
   - Implementar IA en un proceso específico (ej. aprobación de préstamos).
   - Medir reducción de tiempos y errores.

2. **Escalabilidad**
   - Extender la solución a otras áreas (apertura de cuentas, cumplimiento).
   - Integrar con Tabot para soporte al cliente.

3. **Capacitación**
   - Entrenar al equipo en herramientas de IA y mantenimiento de modelos.

4. **Cumplimiento**
   - Asegurar alineación con regulaciones financieras locales e internacionales.

---

## Conclusión

La implementación de agentes de IA en el BPO documental de Bancolombia es una estrategia prometedora para optimizar procesos, reducir costos y mejorar la experiencia del cliente. Con tecnologías como OCR, aprendizaje automático y NLP, y considerando desafíos como la seguridad y la integración, Bancolombia puede posicionarse como líder en innovación bancaria.

---

## Referencias

- [Ailleron: AI Document Processing](https://ailleron.com/insights/ai-document-processing/)
- [AWS: Automate Data Extraction](https://aws.amazon.com/ai/generative-ai/use-cases/document-processing/)
- [Bancolombia: Centro de Competencias IA](https://www.bancolombia.com/acerca-de/sala-prensa/noticias/innovacion/centro-de-competencias-inteligencia-artificial)
- [ResearchGate: AI-Driven Document Processing](https://www.researchgate.net/publication/388619992_AI-driven_intelligent_document_processing_for_banking_and_finance)
