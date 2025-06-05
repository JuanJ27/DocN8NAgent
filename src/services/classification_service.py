"""
Servicio de clasificación de documentos usando modelos de ML
"""
import re
import pickle
from pathlib import Path
from typing import Dict, List, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np
from loguru import logger

from src.models.schemas import DocumentType, ClassificationResult
from src.core.config import DOCUMENT_TYPES, MODEL_CONFIG, MODELS_DIR


class DocumentClassifier:
    """Clasificador de documentos bancarios"""
    
    def __init__(self):
        self.model = None
        self.model_path = MODELS_DIR / "document_classifier.pkl"
        self.patterns = self._create_document_patterns()
        
    def _create_document_patterns(self) -> Dict[DocumentType, List[str]]:
        """Crea patrones de texto para cada tipo de documento"""
        return {
            DocumentType.CEDULA: [
                "cédula", "ciudadanía", "documento de identidad", "CC", "número de documento",
                "lugar de expedición", "fecha de nacimiento", "registraduría"
            ],
            DocumentType.PASAPORTE: [
                "pasaporte", "passport", "república de colombia", "tipo P", "lugar de nacimiento",
                "nacionalidad", "fecha de expedición", "cancillería"
            ],
            DocumentType.RUT: [
                "rut", "registro único tributario", "dian", "actividad económica", "nit",
                "contribuyente", "régimen tributario", "responsabilidades"
            ],
            DocumentType.ESTADO_CUENTA: [
                "estado de cuenta", "extracto bancario", "saldo", "movimientos", "transacciones",
                "débitos", "créditos", "fecha de corte", "banco", "cuenta"
            ],
            DocumentType.CARTA_LABORAL: [
                "carta laboral", "certificación laboral", "empresa", "empleado", "cargo",
                "salario", "fecha de ingreso", "recursos humanos", "contrato de trabajo"
            ],
            DocumentType.DECLARACION_RENTA: [
                "declaración de renta", "formulario 210", "año gravable", "patrimonio",
                "ingresos", "deducciones", "retenciones", "impuesto", "dian"
            ],
            DocumentType.SOLICITUD_CREDITO: [
                "solicitud de crédito", "préstamo", "financiación", "monto solicitado",
                "plazo", "cuotas", "ingresos mensuales", "referencias comerciales"
            ],
            DocumentType.CONTRATO: [
                "contrato", "acuerdo", "partes", "cláusulas", "obligaciones", "términos",
                "condiciones", "firmantes", "testigos"
            ]
        }
    
    def _extract_features(self, text: str) -> Dict[str, float]:
        """Extrae características del texto para clasificación"""
        text_lower = text.lower()
        features = {}
        
        # Características basadas en patrones
        for doc_type, patterns in self.patterns.items():
            pattern_score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    pattern_score += 1
            features[f"pattern_{doc_type.value}"] = pattern_score / len(patterns)
        
        # Características de formato
        features["has_numbers"] = len(re.findall(r'\d+', text)) / len(text.split())
        features["has_dates"] = len(re.findall(r'\d{1,2}/\d{1,2}/\d{4}', text)) > 0
        features["has_currency"] = len(re.findall(r'\$[\d,]+', text)) > 0
        features["line_count"] = len(text.split('\n'))
        features["word_count"] = len(text.split())
        
        return features
    
    def classify_by_patterns(self, text: str) -> ClassificationResult:
        """Clasifica documento usando patrones de texto"""
        scores = {}
        
        for doc_type, patterns in self.patterns.items():
            score = 0
            text_lower = text.lower()
            
            for pattern in patterns:
                if pattern in text_lower:
                    # Dar más peso a patrones más específicos
                    weight = len(pattern.split()) / 10 + 0.1
                    score += weight
            
            # Normalizar score
            scores[doc_type] = score / len(patterns)
        
        # Encontrar el tipo con mayor score
        best_type = max(scores.keys(), key=lambda x: scores[x])
        confidence = scores[best_type]
        
        # Aplicar umbral mínimo de confianza
        if confidence < 0.1:
            # Si no hay suficiente confianza, intentar clasificación por contenido general
            if "banco" in text.lower() or "cuenta" in text.lower():
                best_type = DocumentType.ESTADO_CUENTA
                confidence = 0.5
            else:
                best_type = DocumentType.CEDULA  # Tipo por defecto
                confidence = 0.3
        
        return ClassificationResult(
            document_type=best_type,
            confidence=min(confidence, 1.0),
            reasoning=f"Clasificado por patrones. Scores: {scores}"
        )
    
    def train_ml_model(self, training_data: List[Dict]) -> None:
        """Entrena un modelo de ML para clasificación"""
        try:
            if not training_data:
                logger.warning("No hay datos de entrenamiento disponibles")
                return
            
            # Preparar datos
            texts = [item['text'] for item in training_data]
            labels = [item['document_type'] for item in training_data]
            
            # Crear pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )),
                ('classifier', MultinomialNB())
            ])
            
            # Dividir datos
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=0.2, random_state=42
            )
            
            # Entrenar
            self.model.fit(X_train, y_train)
            
            # Evaluar
            predictions = self.model.predict(X_test)
            report = classification_report(y_test, predictions)
            logger.info(f"Reporte de clasificación:\n{report}")
            
            # Guardar modelo
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            logger.info(f"Modelo entrenado y guardado en {self.model_path}")
            
        except Exception as e:
            logger.error(f"Error entrenando modelo: {e}")
    
    def load_model(self) -> bool:
        """Carga el modelo entrenado"""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info("Modelo de clasificación cargado exitosamente")
                return True
            else:
                logger.warning("No se encontró modelo entrenado")
                return False
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def classify_with_ml(self, text: str) -> ClassificationResult:
        """Clasifica documento usando modelo de ML"""
        if not self.model:
            logger.warning("Modelo no disponible, usando clasificación por patrones")
            return self.classify_by_patterns(text)
        
        try:
            # Predecir
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            
            # Obtener confianza
            max_prob_idx = np.argmax(probabilities)
            confidence = probabilities[max_prob_idx]
            
            return ClassificationResult(
                document_type=DocumentType(prediction),
                confidence=confidence,
                reasoning=f"Clasificado con modelo ML. Probabilidades: {dict(zip(self.model.classes_, probabilities))}"
            )
            
        except Exception as e:
            logger.error(f"Error en clasificación ML: {e}")
            return self.classify_by_patterns(text)
    
    def classify(self, text: str, use_ml: bool = True) -> ClassificationResult:
        """
        Clasifica un documento basado en su texto
        
        Args:
            text: Texto extraído del documento
            use_ml: Si usar modelo de ML (si está disponible) o solo patrones
        """
        if use_ml and self.model:
            return self.classify_with_ml(text)
        else:
            return self.classify_by_patterns(text)
