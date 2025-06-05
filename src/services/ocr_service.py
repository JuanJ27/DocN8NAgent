"""
Servicio de OCR para extracción de texto de documentos
"""
import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image
from typing import Dict, Optional, Tuple
from loguru import logger

from src.core.config import DOCUMENT_CONFIG


class OCRService:
    """Servicio de reconocimiento óptico de caracteres"""
    
    def __init__(self):
        self.tesseract_config = '--oem 3 --psm 6 -l spa'
        self.easyocr_reader = easyocr.Reader(['es', 'en'])
        
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocesa la imagen para mejorar la calidad del OCR"""
        try:
            # Cargar imagen
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar filtro de ruido
            denoised = cv2.medianBlur(gray, 3)
            
            # Mejorar contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Binarización adaptativa
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            return binary
            
        except Exception as e:
            logger.error(f"Error en preprocesamiento de imagen: {e}")
            raise
    
    def extract_with_tesseract(self, image_path: str) -> Dict[str, any]:
        """Extrae texto usando Tesseract OCR"""
        try:
            # Preprocesar imagen
            processed_image = self.preprocess_image(image_path)
            
            # Extraer texto
            text = pytesseract.image_to_string(
                processed_image, 
                config=self.tesseract_config
            )
            
            # Obtener datos detallados
            data = pytesseract.image_to_data(
                processed_image, 
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calcular confianza promedio
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence / 100.0,
                'word_count': len(text.split()),
                'method': 'tesseract'
            }
            
        except Exception as e:
            logger.error(f"Error en OCR con Tesseract: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'word_count': 0,
                'method': 'tesseract',
                'error': str(e)
            }
    
    def extract_with_easyocr(self, image_path: str) -> Dict[str, any]:
        """Extrae texto usando EasyOCR"""
        try:
            # Extraer texto
            results = self.easyocr_reader.readtext(image_path)
            
            # Combinar texto y calcular confianza
            text_parts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                text_parts.append(text)
                confidences.append(confidence)
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': full_text.strip(),
                'confidence': avg_confidence,
                'word_count': len(full_text.split()),
                'method': 'easyocr',
                'bounding_boxes': results
            }
            
        except Exception as e:
            logger.error(f"Error en OCR con EasyOCR: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'word_count': 0,
                'method': 'easyocr',
                'error': str(e)
            }
    
    def extract_text(self, image_path: str, method: str = 'best') -> Dict[str, any]:
        """
        Extrae texto de una imagen usando el método especificado
        
        Args:
            image_path: Ruta a la imagen
            method: 'tesseract', 'easyocr' o 'best' (usa ambos y elige el mejor)
        """
        if method == 'tesseract':
            return self.extract_with_tesseract(image_path)
        elif method == 'easyocr':
            return self.extract_with_easyocr(image_path)
        elif method == 'best':
            # Usar ambos métodos y elegir el mejor resultado
            tesseract_result = self.extract_with_tesseract(image_path)
            easyocr_result = self.extract_with_easyocr(image_path)
            
            # Elegir basado en confianza y cantidad de texto
            if tesseract_result['confidence'] > easyocr_result['confidence']:
                if tesseract_result['word_count'] >= easyocr_result['word_count'] * 0.8:
                    return tesseract_result
            
            return easyocr_result if easyocr_result['word_count'] > 0 else tesseract_result
        else:
            raise ValueError(f"Método no soportado: {method}")
    
    def extract_from_pdf(self, pdf_path: str, page_num: int = 0) -> Dict[str, any]:
        """Extrae texto de una página específica de un PDF"""
        try:
            from pdf2image import convert_from_path
            
            # Convertir página PDF a imagen
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
            
            if not images:
                raise ValueError(f"No se pudo convertir la página {page_num} del PDF")
            
            # Guardar temporalmente la imagen
            temp_image_path = f"/tmp/pdf_page_{page_num}.png"
            images[0].save(temp_image_path, 'PNG')
            
            # Extraer texto
            result = self.extract_text(temp_image_path)
            result['source'] = f"PDF página {page_num}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error extrayendo texto de PDF: {e}")
            return {
                'text': '',
                'confidence': 0.0,
                'word_count': 0,
                'method': 'pdf_ocr',
                'error': str(e)
            }
