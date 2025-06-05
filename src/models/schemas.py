"""
Modelos de datos para el sistema DocN8NAgent
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Tipos de documentos soportados"""
    CEDULA = "cedula"
    PASAPORTE = "pasaporte"
    LICENCIA = "licencia"
    RUT = "rut"
    ESTADO_CUENTA = "estado_cuenta"
    CARTA_LABORAL = "carta_laboral"
    DECLARACION_RENTA = "declaracion_renta"
    SOLICITUD_CREDITO = "solicitud_credito"
    CONTRATO = "contrato"
    PAGARE = "pagare"


class ProcessingStatus(str, Enum):
    """Estados de procesamiento"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class Document(BaseModel):
    """Modelo base para documentos"""
    id: str = Field(..., description="ID único del documento")
    filename: str = Field(..., description="Nombre del archivo")
    file_path: str = Field(..., description="Ruta del archivo")
    document_type: Optional[DocumentType] = Field(None, description="Tipo de documento")
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    uploaded_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    file_size: int = Field(..., description="Tamaño del archivo en bytes")
    mime_type: str = Field(..., description="Tipo MIME del archivo")


class ClassificationResult(BaseModel):
    """Resultado de clasificación de documento"""
    document_type: DocumentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class ExtractionResult(BaseModel):
    """Resultado de extracción de datos"""
    fields: Dict[str, Any] = Field(default_factory=dict)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    raw_text: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None


class ValidationResult(BaseModel):
    """Resultado de validación"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    compliance_score: float = Field(..., ge=0.0, le=1.0)


class FraudDetectionResult(BaseModel):
    """Resultado de detección de fraudes"""
    is_fraudulent: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_factors: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class ProcessingResult(BaseModel):
    """Resultado completo del procesamiento"""
    document: Document
    classification: Optional[ClassificationResult] = None
    extraction: Optional[ExtractionResult] = None
    validation: Optional[ValidationResult] = None
    fraud_detection: Optional[FraudDetectionResult] = None
    processing_time: Optional[float] = None
    errors: List[str] = Field(default_factory=list)


class AgentRequest(BaseModel):
    """Solicitud para el agente de procesamiento"""
    document_id: str
    actions: List[str] = Field(default=["classify", "extract", "validate", "detect_fraud"])
    priority: int = Field(default=1, ge=1, le=5)
    callback_url: Optional[str] = None


class AgentResponse(BaseModel):
    """Respuesta del agente de procesamiento"""
    request_id: str
    status: ProcessingStatus
    result: Optional[ProcessingResult] = None
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
