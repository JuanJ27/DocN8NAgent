"""
API REST para el sistema DocN8NAgent
"""
import os
import uuid
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from src.agents.document_agent import DocumentProcessingAgent
from src.models.schemas import (
    Document, AgentRequest, AgentResponse, ProcessingResult,
    ProcessingStatus, DocumentType
)
from src.core.config import API_CONFIG, DOCUMENT_CONFIG, DATA_DIR

# Configurar logging
logger.add("logs/api.log", rotation="1 day", retention="30 days")

# Crear aplicación FastAPI
app = FastAPI(
    title="DocN8NAgent API",
    description="API para procesamiento inteligente de documentos bancarios",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar agente
agent = DocumentProcessingAgent()

# Almacenamiento en memoria para documentos (en producción usar base de datos)
documents_db: dict = {}
results_db: dict = {}


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "DocN8NAgent API",
        "version": "1.0.0",
        "description": "Sistema de procesamiento inteligente de documentos bancarios"
    }


@app.get("/health")
async def health_check():
    """Verificación de salud del sistema"""
    return {
        "status": "healthy",
        "agent_ready": True,
        "supported_formats": DOCUMENT_CONFIG["supported_formats"]
    }


@app.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...)):
    """
    Sube un documento al sistema
    """
    try:
        # Validar formato
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in DOCUMENT_CONFIG["supported_formats"]:
            raise HTTPException(
                status_code=400,
                detail=f"Formato no soportado: {file_extension}"
            )
        
        # Validar tamaño
        if file.size > DOCUMENT_CONFIG["max_file_size"]:
            raise HTTPException(
                status_code=400,
                detail=f"Archivo demasiado grande. Máximo: {DOCUMENT_CONFIG['max_file_size']} bytes"
            )
        
        # Generar ID único
        document_id = str(uuid.uuid4())
        
        # Guardar archivo
        upload_dir = DATA_DIR / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / f"{document_id}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Crear registro del documento
        document = Document(
            id=document_id,
            filename=file.filename,
            file_path=str(file_path),
            file_size=file.size,
            mime_type=file.content_type or "application/octet-stream"
        )
        
        documents_db[document_id] = document
        
        logger.info(f"Documento subido: {document_id} - {file.filename}")
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "uploaded",
            "message": "Documento subido exitosamente"
        }
        
    except Exception as e:
        logger.error(f"Error subiendo documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/{document_id}", response_model=AgentResponse)
async def process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    actions: Optional[List[str]] = None
):
    """
    Procesa un documento usando el agente de IA
    """
    try:
        if document_id not in documents_db:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        
        document = documents_db[document_id]
        
        if actions is None:
            actions = ["classify", "extract", "validate", "detect_fraud"]
        
        # Crear solicitud
        request = AgentRequest(
            document_id=document_id,
            actions=actions
        )
        
        # Procesar en background
        background_tasks.add_task(process_document_background, document, actions)
        
        return AgentResponse(
            request_id=document_id,
            status=ProcessingStatus.PROCESSING,
            result=None,
            message="Procesamiento iniciado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error iniciando procesamiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_document_background(document: Document, actions: List[str]):
    """Procesa documento en background"""
    try:
        result = await agent.process_document(document, actions)
        results_db[document.id] = result
        documents_db[document.id] = document  # Actualizar estado
        
        logger.info(f"Procesamiento completado para documento {document.id}")
        
    except Exception as e:
        logger.error(f"Error en procesamiento background: {e}")
        document.status = ProcessingStatus.FAILED


@app.get("/status/{document_id}")
async def get_document_status(document_id: str):
    """
    Obtiene el estado de procesamiento de un documento
    """
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    document = documents_db[document_id]
    result = results_db.get(document_id)
    
    response_data = {
        "document_id": document_id,
        "status": document.status,
        "filename": document.filename,
        "uploaded_at": document.uploaded_at,
        "processed_at": document.processed_at
    }
    
    if result:
        response_data["result"] = result
    
    return response_data


@app.get("/result/{document_id}", response_model=ProcessingResult)
async def get_processing_result(document_id: str):
    """
    Obtiene el resultado completo del procesamiento
    """
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    if document_id not in results_db:
        raise HTTPException(status_code=404, detail="Resultado no disponible")
    
    return results_db[document_id]


@app.get("/documents")
async def list_documents():
    """
    Lista todos los documentos en el sistema
    """
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "status": doc.status,
                "document_type": doc.document_type,
                "uploaded_at": doc.uploaded_at
            }
            for doc in documents_db.values()
        ],
        "total": len(documents_db)
    }


@app.delete("/document/{document_id}")
async def delete_document(document_id: str):
    """
    Elimina un documento del sistema
    """
    if document_id not in documents_db:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    
    document = documents_db[document_id]
    
    # Eliminar archivo físico
    try:
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
    except Exception as e:
        logger.warning(f"Error eliminando archivo físico: {e}")
    
    # Eliminar de bases de datos
    del documents_db[document_id]
    if document_id in results_db:
        del results_db[document_id]
    
    return {"message": "Documento eliminado exitosamente"}


@app.get("/stats")
async def get_statistics():
    """
    Obtiene estadísticas del sistema
    """
    total_docs = len(documents_db)
    status_counts = {}
    type_counts = {}
    
    for doc in documents_db.values():
        status_counts[doc.status] = status_counts.get(doc.status, 0) + 1
        if doc.document_type:
            type_counts[doc.document_type] = type_counts.get(doc.document_type, 0) + 1
    
    return {
        "total_documents": total_docs,
        "status_distribution": status_counts,
        "type_distribution": type_counts,
        "success_rate": status_counts.get(ProcessingStatus.COMPLETED, 0) / total_docs if total_docs > 0 else 0
    }


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        reload=API_CONFIG["reload"],
        log_level=API_CONFIG["log_level"]
    )
