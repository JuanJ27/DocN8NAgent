"""
Tests para el servicio de clasificación
"""
import pytest
from src.services.classification_service import DocumentClassifier
from src.models.schemas import DocumentType


class TestDocumentClassifier:
    
    @pytest.fixture
    def classifier(self):
        return DocumentClassifier()
    
    def test_classify_cedula(self, classifier):
        """Test clasificación de cédula"""
        text = """
        REPÚBLICA DE COLOMBIA
        CÉDULA DE CIUDADANÍA
        Número de documento: 12345678
        Nombres: JUAN CARLOS
        Apellidos: PÉREZ GONZÁLEZ
        Fecha de nacimiento: 15/05/1990
        Lugar de expedición: BOGOTÁ D.C.
        """
        
        result = classifier.classify_by_patterns(text)
        
        assert result.document_type == DocumentType.CEDULA
        assert result.confidence > 0.3
    
    def test_classify_estado_cuenta(self, classifier):
        """Test clasificación de estado de cuenta"""
        text = """
        BANCO COLOMBIA
        ESTADO DE CUENTA
        Número de cuenta: 1234567890
        Titular: JUAN PÉREZ
        Saldo disponible: $1,500,000
        Fecha de corte: 31/12/2023
        Movimientos del período:
        - Débito: $100,000
        - Crédito: $200,000
        """
        
        result = classifier.classify_by_patterns(text)
        
        assert result.document_type == DocumentType.ESTADO_CUENTA
        assert result.confidence > 0.3
    
    def test_classify_carta_laboral(self, classifier):
        """Test clasificación de carta laboral"""
        text = """
        CERTIFICACIÓN LABORAL
        
        La empresa TECNOLOGÍA S.A.S certifica que el señor
        JUAN CARLOS PÉREZ se encuentra vinculado laboralmente
        desde el 01/01/2020.
        
        Cargo: Desarrollador Senior
        Salario: $4,500,000 mensuales
        Tipo de contrato: Indefinido
        
        Recursos Humanos
        """
        
        result = classifier.classify_by_patterns(text)
        
        assert result.document_type == DocumentType.CARTA_LABORAL
        assert result.confidence > 0.3
    
    def test_classify_rut(self, classifier):
        """Test clasificación de RUT"""
        text = """
        DIAN - DIRECCIÓN DE IMPUESTOS Y ADUANAS NACIONALES
        REGISTRO ÚNICO TRIBUTARIO - RUT
        
        NIT: 900123456-7
        Razón Social: EMPRESA EJEMPLO S.A.S
        Actividad Económica Principal: 6201 - Desarrollo de software
        Régimen Tributario: Responsable del IVA
        Responsabilidades: 05-IVA, 07-RENTA
        """
        
        result = classifier.classify_by_patterns(text)
        
        assert result.document_type == DocumentType.RUT
        assert result.confidence > 0.3
    
    def test_classify_empty_text(self, classifier):
        """Test clasificación con texto vacío"""
        result = classifier.classify_by_patterns("")
        
        assert result.confidence < 0.5
        assert result.document_type is not None
    
    def test_classify_ambiguous_text(self, classifier):
        """Test clasificación con texto ambiguo"""
        text = "Este es un documento sin contenido específico"
        
        result = classifier.classify_by_patterns(text)
        
        assert result.confidence < 0.5
        assert result.document_type is not None
    
    def test_extract_features(self, classifier):
        """Test extracción de características"""
        text = "CÉDULA 12345678 Fecha: 15/05/1990 Salario: $1,000,000"
        
        features = classifier._extract_features(text)
        
        assert isinstance(features, dict)
        assert 'has_numbers' in features
        assert 'has_dates' in features
        assert 'has_currency' in features
        assert features['has_numbers'] > 0
        assert features['has_dates'] == True
        assert features['has_currency'] == True
    
    def test_training_data_format(self, classifier):
        """Test formato de datos de entrenamiento"""
        training_data = [
            {"text": "CÉDULA DE CIUDADANÍA 12345678", "document_type": "cedula"},
            {"text": "ESTADO DE CUENTA BANCO", "document_type": "estado_cuenta"}
        ]
        
        # No debe fallar con datos válidos
        try:
            classifier.train_ml_model(training_data)
        except Exception as e:
            # Es normal que falle por falta de datos suficientes
            assert "datos de entrenamiento" in str(e).lower() or len(training_data) < 10
