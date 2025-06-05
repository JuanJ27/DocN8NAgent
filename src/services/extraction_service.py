"""
Servicio de extracción de datos de documentos usando NLP
"""
import re
import spacy
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger

from src.models.schemas import DocumentType, ExtractionResult
from src.core.config import EXTRACTION_FIELDS


class DataExtractionService:
    """Servicio de extracción de datos estructurados de documentos"""
    
    def __init__(self):
        try:
            # Cargar modelo de spaCy para español
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            logger.warning("Modelo spaCy no encontrado. Usando extracción basada en regex")
            self.nlp = None
        
        self.patterns = self._create_extraction_patterns()
    
    def _create_extraction_patterns(self) -> Dict[str, Dict[str, str]]:
        """Crea patrones regex para extracción de campos específicos"""
        return {
            "cedula": {
                "numero_documento": r"(?:CC|C\.C\.|Cédula|Documento)\s*:?\s*(\d{6,12})",
                "nombres": r"(?:Nombres?|Apellidos?\s+y\s+Nombres?)\s*:?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
                "fecha_nacimiento": r"(?:Fecha\s+de\s+nacimiento|Nacimiento)\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})",
                "lugar_expedicion": r"(?:Lugar\s+de\s+expedición|Expedida\s+en)\s*:?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s,]+)"
            },
            "estado_cuenta": {
                "numero_cuenta": r"(?:Cuenta|Número\s+de\s+cuenta)\s*:?\s*(\d{10,20})",
                "titular": r"(?:Titular|Cliente)\s*:?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
                "saldo": r"(?:Saldo|Disponible)\s*:?\s*\$?([\d,]+\.?\d*)",
                "fecha_corte": r"(?:Fecha\s+de\s+corte|Corte)\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})"
            },
            "carta_laboral": {
                "empleado": r"(?:Empleado|Trabajador|Señor|Señora)\s*:?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
                "empresa": r"(?:Empresa|Compañía|Razón\s+social)\s*:?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s&.,]+)",
                "cargo": r"(?:Cargo|Posición|Desempeña)\s*:?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
                "salario": r"(?:Salario|Sueldo|Ingresos?)\s*:?\s*\$?([\d,]+\.?\d*)",
                "fecha_ingreso": r"(?:Fecha\s+de\s+ingreso|Ingresó)\s*:?\s*(\d{1,2}/\d{1,2}/\d{4})"
            },
            "solicitud_credito": {
                "solicitante": r"(?:Solicitante|Cliente|Nombres?)\s*:?\s*([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)",
                "monto": r"(?:Monto|Valor|Crédito)\s*:?\s*\$?([\d,]+\.?\d*)",
                "plazo": r"(?:Plazo|Término|Cuotas)\s*:?\s*(\d+)\s*(?:meses?|años?)",
                "ingresos": r"(?:Ingresos?\s+mensuales?|Salario)\s*:?\s*\$?([\d,]+\.?\d*)"
            }
        }
    
    def extract_with_regex(self, text: str, document_type: DocumentType) -> Dict[str, Any]:
        """Extrae datos usando expresiones regulares"""
        extracted_data = {}
        confidence_scores = {}
        
        # Obtener patrones para el tipo de documento
        doc_patterns = self.patterns.get(document_type.value, {})
        
        for field, pattern in doc_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            
            if matches:
                # Tomar la primera coincidencia
                value = matches[0].strip()
                
                # Limpiar y formatear el valor
                if field in ["numero_documento", "numero_cuenta"]:
                    value = re.sub(r'[^\d]', '', value)
                elif field in ["saldo", "salario", "monto", "ingresos"]:
                    value = re.sub(r'[^\d,.]', '', value)
                elif field in ["fecha_nacimiento", "fecha_corte", "fecha_ingreso"]:
                    value = self._normalize_date(value)
                
                extracted_data[field] = value
                confidence_scores[field] = 0.8  # Confianza fija para regex
        
        return extracted_data, confidence_scores
    
    def extract_with_nlp(self, text: str, document_type: DocumentType) -> Dict[str, Any]:
        """Extrae datos usando procesamiento de lenguaje natural"""
        if not self.nlp:
            return {}, {}
        
        extracted_data = {}
        confidence_scores = {}
        
        # Procesar texto con spaCy
        doc = self.nlp(text)
        
        # Extraer entidades nombradas
        for ent in doc.ents:
            if ent.label_ == "PER":  # Personas
                if "nombres" not in extracted_data:
                    extracted_data["nombres"] = ent.text
                    confidence_scores["nombres"] = 0.7
                elif "empleado" not in extracted_data:
                    extracted_data["empleado"] = ent.text
                    confidence_scores["empleado"] = 0.7
                    
            elif ent.label_ == "ORG":  # Organizaciones
                if "empresa" not in extracted_data:
                    extracted_data["empresa"] = ent.text
                    confidence_scores["empresa"] = 0.7
                    
            elif ent.label_ == "MONEY":  # Cantidades monetarias
                money_value = re.sub(r'[^\d,.]', '', ent.text)
                if "saldo" not in extracted_data and document_type == DocumentType.ESTADO_CUENTA:
                    extracted_data["saldo"] = money_value
                    confidence_scores["saldo"] = 0.6
                elif "salario" not in extracted_data and document_type == DocumentType.CARTA_LABORAL:
                    extracted_data["salario"] = money_value
                    confidence_scores["salario"] = 0.6
        
        # Extraer fechas usando patrones
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text)
            for date in dates:
                normalized_date = self._normalize_date(date)
                if normalized_date and "fecha_nacimiento" not in extracted_data:
                    extracted_data["fecha_nacimiento"] = normalized_date
                    confidence_scores["fecha_nacimiento"] = 0.6
                    break
        
        return extracted_data, confidence_scores
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normaliza fechas a formato DD/MM/YYYY"""
        try:
            # Intentar diferentes formatos
            formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%d/%m/%Y')
                except ValueError:
                    continue
            
            # Intentar formato con nombres de meses en español
            months = {
                'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
            }
            
            # Patrón: "día de mes de año"
            pattern = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
            match = re.search(pattern, date_str.lower())
            
            if match:
                day, month_name, year = match.groups()
                month_num = months.get(month_name.lower())
                if month_num:
                    return f"{day.zfill(2)}/{month_num}/{year}"
            
            return None
            
        except Exception as e:
            logger.warning(f"Error normalizando fecha '{date_str}': {e}")
            return None
    
    def extract_data(self, text: str, document_type: DocumentType, use_nlp: bool = True) -> ExtractionResult:
        """
        Extrae datos estructurados de un documento
        
        Args:
            text: Texto del documento
            document_type: Tipo de documento
            use_nlp: Si usar NLP además de regex
        """
        try:
            # Extracción con regex
            regex_data, regex_scores = self.extract_with_regex(text, document_type)
            
            # Extracción con NLP (si está disponible)
            nlp_data, nlp_scores = {}, {}
            if use_nlp:
                nlp_data, nlp_scores = self.extract_with_nlp(text, document_type)
            
            # Combinar resultados, priorizando regex
            combined_data = {**nlp_data, **regex_data}
            combined_scores = {**nlp_scores, **regex_scores}
            
            # Crear estructura de datos específica para el tipo de documento
            expected_fields = EXTRACTION_FIELDS.get(document_type.value, [])
            structured_data = {}
            
            for field in expected_fields:
                if field in combined_data:
                    structured_data[field] = combined_data[field]
            
            return ExtractionResult(
                fields=combined_data,
                confidence_scores=combined_scores,
                raw_text=text[:500] + "..." if len(text) > 500 else text,
                structured_data=structured_data
            )
            
        except Exception as e:
            logger.error(f"Error en extracción de datos: {e}")
            return ExtractionResult(
                fields={},
                confidence_scores={},
                raw_text=text[:500] + "..." if len(text) > 500 else text,
                structured_data={}
            )
