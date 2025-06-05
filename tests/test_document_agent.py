"""
Tests para el agente principal de documentos
"""
import pytest
import asyncio
import tempfile
from unittest.mock import Mock, AsyncMock
from pathlib import Path

from src.agents.document_agent import DocumentProcessingAgent
from src.models.schemas import Document, ProcessingStatus, DocumentType


class TestDocumentProcessingAgent:
    
    @pytest.fixture
    def agent(self):
        return DocumentProcessingAgent()
    
    @pytest.fixture
    def sample_document(self):
        """Crea un documento de prueba"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b"CEDULA DE CIUDADANIA\nNumero: 12345678\nNombres: JUAN PEREZ")
        temp_file.close()
        
        return Document(
            id="test_doc_1",
            filename="test.txt",
            file_path=temp_file.name,
            file_size=50,
            mime_type="text/plain"
        )
    
    @pytest.mark.asyncio
    async def test_process_document_success(self, agent, sample_document):
        """Test procesamiento exitoso de documento"""
        result = await agent.process_document(sample_document, ['classify'])
        
        assert result is not None
        assert sample_document.status in [ProcessingStatus.COMPLETED, ProcessingStatus.PROCESSING]
        assert result.processing_time is not None
    
    @pytest.mark.asyncio
    async def test_process_document_all_actions(self, agent, sample_document):
        """Test procesamiento con todas las acciones"""
        actions = ['classify', 'extract', 'validate', 'detect_fraud']
        result = await agent.process_document(sample_document, actions)
        
        assert result.classification is not None
        assert result.extraction is not None
        assert result.validation is not None
        assert result.fraud_detection is not None
    
    @pytest.mark.asyncio
    async def test_extract_text_invalid_file(self, agent):
        """Test extracción de texto con archivo inválido"""
        invalid_doc = Document(
            id="invalid",
            filename="nonexistent.pdf",
            file_path="/path/that/does/not/exist.pdf",
            file_size=0,
            mime_type="application/pdf"
        )
        
        text = await agent._extract_text(invalid_doc)
        assert text is None or text == ""
    
    def test_classify_document(self, agent):
        """Test clasificación de documento"""
        text = "CEDULA DE CIUDADANIA Numero: 12345678"
        result = agent._classify_document(text)
        
        assert result.document_type == DocumentType.CEDULA
        assert 0 <= result.confidence <= 1
    
    def test_extract_data(self, agent):
        """Test extracción de datos"""
        text = "CEDULA DE CIUDADANIA Numero: 12345678 Nombres: JUAN PEREZ"
        result = agent._extract_data(text, DocumentType.CEDULA)
        
        assert result is not None
        assert isinstance(result.fields, dict)
    
    def test_validate_document(self, agent):
        """Test validación de documento"""
        from src.models.schemas import ExtractionResult
        
        extraction = ExtractionResult(
            fields={"numero_documento": "12345678", "nombres": "JUAN PEREZ"},
            confidence_scores={"numero_documento": 0.9, "nombres": 0.8}
        )
        
        result = agent._validate_document(extraction, DocumentType.CEDULA)
        
        assert result.is_valid == True
        assert 0 <= result.compliance_score <= 1
    
    def test_detect_fraud(self, agent):
        """Test detección de fraudes"""
        from src.models.schemas import ExtractionResult
        
        text = "CEDULA DE CIUDADANIA"
        extraction = ExtractionResult(
            fields={"numero_documento": "12345678"},
            confidence_scores={"numero_documento": 0.9}
        )
        
        result = agent._detect_fraud(text, extraction)
        
        assert isinstance(result.is_fraudulent, bool)
        assert 0 <= result.risk_score <= 1
        assert isinstance(result.risk_factors, list)
    
    def cleanup_temp_files(self, sample_document):
        """Limpia archivos temporales"""
        try:
            Path(sample_document.file_path).unlink()
        except:
            pass
