"""
Tests unitarios para el servicio de OCR
"""
import pytest
import tempfile
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from src.services.ocr_service import OCRService


class TestOCRService:
    
    @pytest.fixture
    def ocr_service(self):
        return OCRService()
    
    @pytest.fixture
    def sample_image(self):
        """Crea una imagen de prueba con texto"""
        # Crear imagen blanca
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Añadir texto
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), "CEDULA DE CIUDADANIA", fill='black', font=font)
        draw.text((10, 50), "Número: 12345678", fill='black', font=font)
        draw.text((10, 90), "Nombres: JUAN PEREZ", fill='black', font=font)
        draw.text((10, 130), "Fecha: 15/05/1990", fill='black', font=font)
        
        # Guardar temporalmente
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        
        return temp_file.name
    
    def test_extract_with_tesseract(self, ocr_service, sample_image):
        """Test extracción con Tesseract"""
        result = ocr_service.extract_with_tesseract(sample_image)
        
        assert 'text' in result
        assert 'confidence' in result
        assert 'method' in result
        assert result['method'] == 'tesseract'
        assert len(result['text']) > 0
        assert 'CEDULA' in result['text'].upper()
    
    def test_extract_with_easyocr(self, ocr_service, sample_image):
        """Test extracción con EasyOCR"""
        result = ocr_service.extract_with_easyocr(sample_image)
        
        assert 'text' in result
        assert 'confidence' in result
        assert 'method' in result
        assert result['method'] == 'easyocr'
        assert 'bounding_boxes' in result
    
    def test_extract_text_best_method(self, ocr_service, sample_image):
        """Test extracción con mejor método"""
        result = ocr_service.extract_text(sample_image, method='best')
        
        assert 'text' in result
        assert 'confidence' in result
        assert len(result['text']) > 0
    
    def test_preprocess_image(self, ocr_service, sample_image):
        """Test preprocesamiento de imagen"""
        processed = ocr_service.preprocess_image(sample_image)
        
        assert processed is not None
        assert isinstance(processed, np.ndarray)
        assert len(processed.shape) == 2  # Imagen en escala de grises
    
    def test_invalid_image_path(self, ocr_service):
        """Test con ruta de imagen inválida"""
        result = ocr_service.extract_text("invalid_path.jpg")
        
        assert result['confidence'] == 0.0
        assert 'error' in result
    
    def test_different_methods(self, ocr_service, sample_image):
        """Test diferentes métodos de extracción"""
        methods = ['tesseract', 'easyocr', 'best']
        
        for method in methods:
            result = ocr_service.extract_text(sample_image, method=method)
            assert 'text' in result
            assert 'confidence' in result
            assert 'method' in result
    
    def test_unsupported_method(self, ocr_service, sample_image):
        """Test método no soportado"""
        with pytest.raises(ValueError):
            ocr_service.extract_text(sample_image, method='unsupported')
    
    def cleanup_temp_files(self, sample_image):
        """Limpia archivos temporales"""
        try:
            Path(sample_image).unlink()
        except:
            pass
