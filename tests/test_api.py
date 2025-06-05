"""
Tests para la API REST
"""
import pytest
import tempfile
import io
from fastapi.testclient import TestClient
from pathlib import Path

from src.api.main import app

client = TestClient(app)


class TestAPI:
    
    def test_root_endpoint(self):
        """Test endpoint raíz"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self):
        """Test verificación de salud"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "supported_formats" in data
    
    def test_upload_document(self):
        """Test subida de documento"""
        # Crear archivo de prueba
        test_content = b"CEDULA DE CIUDADANIA\nNumero: 12345678"
        test_file = io.BytesIO(test_content)
        
        response = client.post(
            "/upload",
            files={"file": ("test.txt", test_file, "text/plain")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["status"] == "uploaded"
        
        return data["document_id"]
    
    def test_upload_invalid_format(self):
        """Test subida con formato inválido"""
        test_content = b"contenido de prueba"
        test_file = io.BytesIO(test_content)
        
        response = client.post(
            "/upload",
            files={"file": ("test.xyz", test_file, "application/octet-stream")}
        )
        
        assert response.status_code == 400
    
    def test_process_document(self):
        """Test procesamiento de documento"""
        # Primero subir un documento
        document_id = self.test_upload_document()
        
        # Procesar documento
        response = client.post(f"/process/{document_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == document_id
        assert data["status"] == "processing"
    
    def test_process_nonexistent_document(self):
        """Test procesamiento de documento inexistente"""
        response = client.post("/process/nonexistent_id")
        assert response.status_code == 404
    
    def test_get_document_status(self):
        """Test obtener estado de documento"""
        # Subir y procesar documento
        document_id = self.test_upload_document()
        client.post(f"/process/{document_id}")
        
        # Obtener estado
        response = client.get(f"/status/{document_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["document_id"] == document_id
        assert "status" in data
    
    def test_list_documents(self):
        """Test listar documentos"""
        response = client.get("/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert "total" in data
        assert isinstance(data["documents"], list)
    
    def test_get_statistics(self):
        """Test obtener estadísticas"""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "status_distribution" in data
        assert "success_rate" in data
    
    def test_delete_document(self):
        """Test eliminar documento"""
        # Subir documento
        document_id = self.test_upload_document()
        
        # Eliminar documento
        response = client.delete(f"/document/{document_id}")
        assert response.status_code == 200
        
        # Verificar que no existe
        response = client.get(f"/status/{document_id}")
        assert response.status_code == 404
