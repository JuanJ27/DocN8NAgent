# Configuración del Sistema DocN8NAgent (CPU Optimizado)
# ============================================================

## 📋 Resumen de la Instalación

✅ **COMPLETADO**: Sistema DocN8NAgent configurado para CPU
✅ **ENTORNO**: Python 3.11.2 en /home/juan/DocN8NAgent/venv
✅ **DEPENDENCIAS**: PyTorch CPU, FastAPI, spaCy, Tesseract OCR
✅ **MODELOS**: es_core_news_sm (spaCy), EasyOCR con modelos automáticos
✅ **DEMO**: Funcionando correctamente con 3 documentos de prueba

## 🔧 Componentes Instalados

### Dependencias Principales (CPU)
- PyTorch 2.7.1+cpu (sin CUDA)
- Transformers 4.52.4
- FastAPI 0.115.12 + Uvicorn
- spaCy 3.8.7 + modelo es_core_news_sm
- OpenCV 4.11.0 (headless)
- Tesseract OCR 5.3.0 + idioma español
- EasyOCR 1.7.2
- scikit-learn 1.6.1 (modelos ML ligeros)

### Servicios del Sistema
- **OCR Service**: Tesseract + EasyOCR con selección automática del mejor resultado
- **Classification Service**: Patrones + ML para clasificar documentos
- **Extraction Service**: Regex + NLP para extraer datos estructurados
- **Document Agent**: Orquestador principal del pipeline de procesamiento

## 📊 Capacidades del Sistema

### Tipos de Documentos Soportados
- ✅ Cédulas de ciudadanía
- ✅ Estados de cuenta bancarios  
- ✅ Cartas laborales
- ✅ Solicitudes de crédito
- ✅ Facturas de servicios públicos

### Formatos Soportados
- PDF (.pdf)
- Imágenes (.png, .jpg, .jpeg, .tiff)
- Documentos Word (.docx)

### Datos Extraídos
- Nombres y apellidos
- Números de documento
- Fechas (nacimiento, expedición, corte)
- Información financiera (salarios, saldos)
- Datos de contacto (direcciones, teléfonos)
- Información empresarial

## 🚀 Comandos de Uso

### Inicio Rápido
```bash
cd /home/juan/DocN8NAgent
source venv/bin/activate
./quick_start.sh demo    # Demostración
./quick_start.sh api     # Servidor API
./quick_start.sh cli     # CLI interactivo
```

### Comandos Directos
```bash
# Activar entorno
source venv/bin/activate

# Ejecutar demo
python demo.py

# Iniciar API (puerto 8000)
python -m src.api.main

# CLI simple
python -m src.cli_simple status
python -m src.cli_simple process archivo.pdf

# CLI completo (con Rich UI)
python -m src.cli process archivo.pdf
python -m src.cli status
python -m src.cli history
```

## 📡 API REST

### Endpoints Principales
- `GET /` - Estado del servicio
- `POST /upload` - Subir documento
- `GET /process/{doc_id}` - Procesar documento
- `GET /status/{doc_id}` - Estado del procesamiento
- `GET /result/{doc_id}` - Obtener resultados
- `GET /docs` - Documentación Swagger

### Ejemplo de Uso
```bash
# Subir documento
curl -X POST "http://localhost:8000/upload" \
     -F "file=@documento.pdf"

# Verificar estado
curl "http://localhost:8000/status/doc_123"

# Obtener resultados
curl "http://localhost:8000/result/doc_123"
```

## ⚡ Optimizaciones para CPU

### Modelos Ligeros
- PyTorch CPU-only (sin CUDA overhead)
- spaCy modelo pequeño (es_core_news_sm)
- scikit-learn para clasificación básica
- OpenCV headless (sin GUI dependencies)

### Procesamiento Eficiente
- OCR en paralelo (Tesseract + EasyOCR)
- Selección automática del mejor resultado
- Cache de modelos para evitar recargas
- Procesamiento por lotes opcional

### Memoria Optimizada
- Liberación automática de memoria
- Modelos compartidos entre procesos
- Límites de tamaño de archivo configurables

## 🔍 Resolución de Problemas

### Errores Comunes

1. **ImportError de torch**
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

2. **Tesseract no encontrado**
   ```bash
   sudo apt-get install tesseract-ocr tesseract-ocr-spa
   ```

3. **Modelo spaCy faltante**
   ```bash
   python -m spacy download es_core_news_sm
   ```

4. **Puerto 8000 ocupado**
   ```bash
   # Cambiar puerto en src/api/main.py
   uvicorn.run(app, host="0.0.0.0", port=8001)
   ```

### Logs y Debugging
- Logs en: `logs/docn8n.log`
- Nivel de log configurable en `src/core/config.py`
- Debug mode: `DOCN8N_DEBUG=true python demo.py`

## 📈 Métricas de Rendimiento

### Tiempos Promedio (CPU)
- OCR por página: 2-5 segundos
- Clasificación: 0.1-0.5 segundos  
- Extracción de datos: 0.5-1 segundo
- **Total por documento**: 3-7 segundos

### Precisión Esperada
- OCR: 85-95% (depende de calidad de imagen)
- Clasificación: 80-90%
- Extracción: 70-85%
- Validación: 90-95%

## 🔄 Próximos Pasos

1. **Entrenamiento de Modelos**: Usar datos reales para mejorar precisión
2. **Integración**: Conectar con sistemas bancarios existentes
3. **Escalabilidad**: Configurar múltiples workers para mayor throughput
4. **Seguridad**: Implementar encriptación y auditoría
5. **Monitoreo**: Métricas en tiempo real y alertas

## 📞 Soporte

Para problemas o preguntas:
1. Verificar logs en `logs/`
2. Ejecutar `python -m src.cli_simple status`
3. Revisar documentación en `/docs`
4. Usar modo debug para más información

---
*DocN8NAgent v1.0 - Optimizado para CPU | Último update: 2025-06-04*
