"""
Script de demostración del sistema DocN8NAgent
"""
import asyncio
import tempfile
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from src.agents.document_agent import DocumentProcessingAgent
from src.models.schemas import Document, ProcessingStatus


async def create_sample_documents():
    """Crea documentos de ejemplo para demostración"""
    documents = []
    
    # 1. Crear cédula de ejemplo
    cedula_img = Image.new('RGB', (600, 400), color='white')
    draw = ImageDraw.Draw(cedula_img)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_text = ImageFont.truetype("arial.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Texto de cédula
    draw.text((50, 30), "REPÚBLICA DE COLOMBIA", fill='black', font=font_title)
    draw.text((50, 60), "CÉDULA DE CIUDADANÍA", fill='black', font=font_title)
    draw.text((50, 120), "Número: 1234567890", fill='black', font=font_text)
    draw.text((50, 150), "Nombres: JUAN CARLOS", fill='black', font=font_text)
    draw.text((50, 180), "Apellidos: PÉREZ GONZÁLEZ", fill='black', font=font_text)
    draw.text((50, 210), "Fecha de nacimiento: 15/05/1990", fill='black', font=font_text)
    draw.text((50, 240), "Lugar de expedición: BOGOTÁ D.C.", fill='black', font=font_text)
    
    cedula_path = "/tmp/cedula_ejemplo.png"
    cedula_img.save(cedula_path)
    
    documents.append({
        "path": cedula_path,
        "type": "cedula",
        "description": "Cédula de ciudadanía"
    })
    
    # 2. Crear estado de cuenta de ejemplo
    cuenta_img = Image.new('RGB', (700, 500), color='white')
    draw = ImageDraw.Draw(cuenta_img)
    
    draw.text((50, 30), "BANCO COLOMBIA", fill='black', font=font_title)
    draw.text((50, 60), "ESTADO DE CUENTA", fill='black', font=font_title)
    draw.text((50, 120), "Número de cuenta: 9876543210", fill='black', font=font_text)
    draw.text((50, 150), "Titular: JUAN CARLOS PÉREZ", fill='black', font=font_text)
    draw.text((50, 180), "Saldo disponible: $2,500,000", fill='black', font=font_text)
    draw.text((50, 210), "Fecha de corte: 31/12/2023", fill='black', font=font_text)
    draw.text((50, 250), "MOVIMIENTOS DEL PERÍODO:", fill='black', font=font_text)
    draw.text((70, 280), "• Nómina empresa: +$3,200,000", fill='black', font=font_text)
    draw.text((70, 310), "• Pago servicios: -$450,000", fill='black', font=font_text)
    draw.text((70, 340), "• Transferencia: -$250,000", fill='black', font=font_text)
    
    cuenta_path = "/tmp/estado_cuenta_ejemplo.png"
    cuenta_img.save(cuenta_path)
    
    documents.append({
        "path": cuenta_path,
        "type": "estado_cuenta", 
        "description": "Estado de cuenta bancario"
    })
    
    # 3. Crear carta laboral de ejemplo
    carta_img = Image.new('RGB', (700, 600), color='white')
    draw = ImageDraw.Draw(carta_img)
    
    draw.text((50, 30), "CERTIFICACIÓN LABORAL", fill='black', font=font_title)
    draw.text((50, 80), "TECNOLOGÍA AVANZADA S.A.S", fill='black', font=font_text)
    draw.text((50, 110), "NIT: 900.123.456-7", fill='black', font=font_text)
    draw.text((50, 150), "La empresa certifica que el señor", fill='black', font=font_text)
    draw.text((50, 180), "JUAN CARLOS PÉREZ GONZÁLEZ", fill='black', font=font_text)
    draw.text((50, 210), "identificado con C.C. 1234567890", fill='black', font=font_text)
    draw.text((50, 240), "se encuentra vinculado laboralmente", fill='black', font=font_text)
    draw.text((50, 270), "desde el 15 de enero de 2020.", fill='black', font=font_text)
    draw.text((50, 320), "Cargo: Desarrollador Senior", fill='black', font=font_text)
    draw.text((50, 350), "Salario básico: $4,500,000 mensuales", fill='black', font=font_text)
    draw.text((50, 380), "Tipo de contrato: Término indefinido", fill='black', font=font_text)
    draw.text((50, 430), "Esta certificación se expide a", fill='black', font=font_text)
    draw.text((50, 460), "solicitud del interesado.", fill='black', font=font_text)
    
    carta_path = "/tmp/carta_laboral_ejemplo.png"
    carta_img.save(carta_path)
    
    documents.append({
        "path": carta_path,
        "type": "carta_laboral",
        "description": "Carta laboral"
    })
    
    return documents


async def demo_processing():
    """Demuestra el procesamiento de documentos"""
    print("🚀 Iniciando demostración de DocN8NAgent")
    print("=" * 50)
    
    # Inicializar agente
    agent = DocumentProcessingAgent()
    
    # Crear documentos de ejemplo
    print("📄 Creando documentos de ejemplo...")
    sample_docs = await create_sample_documents()
    
    # Procesar cada documento
    for i, doc_info in enumerate(sample_docs, 1):
        print(f"\n📋 Procesando documento {i}: {doc_info['description']}")
        print("-" * 40)
        
        # Crear objeto Document
        document = Document(
            id=f"demo_{i}",
            filename=Path(doc_info["path"]).name,
            file_path=doc_info["path"],
            file_size=Path(doc_info["path"]).stat().st_size,
            mime_type="image/png"
        )
        
        # Procesar
        result = await agent.process_document(document)
        
        # Mostrar resultados
        print(f"📊 Estado: {document.status}")
        print(f"⏱️  Tiempo de procesamiento: {result.processing_time:.2f}s")
        
        if result.classification:
            print(f"🏷️  Tipo detectado: {result.classification.document_type}")
            print(f"🎯 Confianza: {result.classification.confidence:.2%}")
        
        if result.extraction and result.extraction.fields:
            print("📋 Datos extraídos:")
            for field, value in result.extraction.fields.items():
                confidence = result.extraction.confidence_scores.get(field, 0)
                print(f"   • {field}: {value} (confianza: {confidence:.2%})")
        
        if result.validation:
            validation_icon = "✅" if result.validation.is_valid else "❌"
            print(f"{validation_icon} Validación: {'Válido' if result.validation.is_valid else 'Inválido'}")
            print(f"📊 Puntuación: {result.validation.compliance_score:.2%}")
            
            if result.validation.errors:
                print("❌ Errores:")
                for error in result.validation.errors:
                    print(f"   • {error}")
            
            if result.validation.warnings:
                print("⚠️  Advertencias:")
                for warning in result.validation.warnings:
                    print(f"   • {warning}")
        
        if result.fraud_detection:
            fraud_icon = "🚨" if result.fraud_detection.is_fraudulent else "🛡️"
            print(f"{fraud_icon} Análisis de fraude: {'Detectado' if result.fraud_detection.is_fraudulent else 'No detectado'}")
            print(f"⚠️  Riesgo: {result.fraud_detection.risk_score:.2%}")
            
            if result.fraud_detection.risk_factors:
                print("🔍 Factores de riesgo:")
                for factor in result.fraud_detection.risk_factors:
                    print(f"   • {factor}")
        
        if result.errors:
            print("❌ Errores en procesamiento:")
            for error in result.errors:
                print(f"   • {error}")
    
    print("\n" + "=" * 50)
    print("✅ Demostración completada")
    print("\n💡 Para probar con tus propios documentos:")
    print("   1. Inicia el servidor: python -m src.api.main")
    print("   2. Usa el CLI: python -m src.cli process tu_documento.pdf")
    print("   3. O usa la API REST directamente")


if __name__ == "__main__":
    asyncio.run(demo_processing())
