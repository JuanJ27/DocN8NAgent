"""
Cliente CLI simple para DocN8NAgent (sin dependencias pesadas)
"""
import sys
import time
import requests
import json
from pathlib import Path
from typing import List, Dict, Any

BASE_URL = "http://localhost:8000"


def print_status(message: str, status: str = "info"):
    """Imprime mensaje con estado"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "processing": "🔄"
    }
    print(f"{icons.get(status, 'ℹ️')} {message}")


def print_table(headers: List[str], rows: List[List[str]], title: str = None):
    """Imprime tabla simple"""
    if title:
        print(f"\n{title}")
        print("=" * len(title))
    
    # Calcular anchos de columna
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Imprimir cabeceras
    header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Imprimir filas
    for row in rows:
        row_str = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(row_str)


def check_service_status():
    """Verifica el estado del servicio"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status("Servicio activo", "success")
            print(f"Formatos soportados: {', '.join(data['supported_formats'])}")
            return True
        else:
            print_status("Servicio no disponible", "error")
            return False
    except Exception as e:
        print_status(f"Error conectando al servicio: {e}", "error")
        return False


def upload_document(file_path: str) -> str:
    """Sube un documento"""
    try:
        if not Path(file_path).exists():
            print_status(f"Archivo no encontrado: {file_path}", "error")
            return None
            
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            response = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
            
            if response.status_code == 200:
                upload_data = response.json()
                document_id = upload_data["document_id"]
                print_status(f"Documento subido: {document_id}", "success")
                return document_id
            else:
                print_status(f"Error subiendo archivo: {response.text}", "error")
                return None
                
    except Exception as e:
        print_status(f"Error: {e}", "error")
        return None


def process_document(document_id: str, actions: List[str] = None) -> bool:
    """Procesa un documento"""
    try:
        process_data = {}
        if actions:
            process_data["actions"] = actions
            
        response = requests.post(
            f"{BASE_URL}/process/{document_id}",
            json=process_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print_status("Procesamiento iniciado", "processing")
            return True
        else:
            print_status(f"Error procesando: {response.text}", "error")
            return False
            
    except Exception as e:
        print_status(f"Error: {e}", "error")
        return False


def wait_for_result(document_id: str, max_wait: int = 60) -> Dict[str, Any]:
    """Espera el resultado del procesamiento"""
    print_status("Esperando resultado...", "processing")
    
    for i in range(max_wait):
        try:
            status_response = requests.get(f"{BASE_URL}/status/{document_id}", timeout=5)
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                if status_data["status"] in ["completed", "failed", "rejected"]:
                    # Obtener resultado completo
                    result_response = requests.get(f"{BASE_URL}/result/{document_id}", timeout=5)
                    if result_response.status_code == 200:
                        return result_response.json()
                    else:
                        print_status("Error obteniendo resultado", "error")
                        return None
                        
                elif i % 5 == 0:  # Imprimir progreso cada 5 segundos
                    print(f"Estado: {status_data['status']} ({i}s)")
                    
            time.sleep(1)
            
        except Exception as e:
            print_status(f"Error verificando estado: {e}", "warning")
            time.sleep(1)
    
    print_status("Tiempo de espera agotado", "warning")
    return None


def display_result(result: Dict[str, Any]):
    """Muestra el resultado del procesamiento"""
    print("\n" + "=" * 50)
    print_status("Resultado del Procesamiento", "success")
    print("=" * 50)
    
    # Información del documento
    doc = result["document"]
    print(f"📄 Archivo: {doc['filename']}")
    print(f"🏷️  Estado: {doc['status']}")
    print(f"⏱️  Tiempo: {result.get('processing_time', 0):.2f}s")
    
    # Clasificación
    if result.get("classification"):
        classification = result["classification"]
        print(f"📂 Tipo: {classification['document_type']}")
        print(f"🎯 Confianza: {classification['confidence']:.2%}")
    
    # Datos extraídos
    if result.get("extraction") and result["extraction"]["fields"]:
        print("\n📋 Datos Extraídos:")
        for field, value in result["extraction"]["fields"].items():
            confidence = result["extraction"]["confidence_scores"].get(field, 0)
            print(f"   • {field}: {value} (confianza: {confidence:.2%})")
    
    # Validación
    if result.get("validation"):
        validation = result["validation"]
        status_icon = "✅" if validation["is_valid"] else "❌"
        print(f"\n{status_icon} Validación: {'Válido' if validation['is_valid'] else 'Inválido'}")
        print(f"📊 Puntuación: {validation['compliance_score']:.2%}")
        
        if validation["errors"]:
            print("❌ Errores:")
            for error in validation["errors"]:
                print(f"   • {error}")
        
        if validation["warnings"]:
            print("⚠️  Advertencias:")
            for warning in validation["warnings"]:
                print(f"   • {warning}")
    
    # Detección de fraudes
    if result.get("fraud_detection"):
        fraud = result["fraud_detection"]
        fraud_icon = "🚨" if fraud["is_fraudulent"] else "🛡️"
        print(f"\n{fraud_icon} Fraude: {'Detectado' if fraud['is_fraudulent'] else 'No detectado'}")
        print(f"⚠️  Riesgo: {fraud['risk_score']:.2%}")
        
        if fraud["risk_factors"]:
            print("🔍 Factores de riesgo:")
            for factor in fraud["risk_factors"]:
                print(f"   • {factor}")


def cmd_status():
    """Comando: verificar estado"""
    check_service_status()


def cmd_process(file_path: str, actions: List[str] = None):
    """Comando: procesar documento"""
    if not check_service_status():
        return
    
    # Subir documento
    document_id = upload_document(file_path)
    if not document_id:
        return
    
    # Procesar
    if not process_document(document_id, actions):
        return
    
    # Esperar resultado
    result = wait_for_result(document_id)
    if result:
        display_result(result)
    else:
        print_status("No se pudo obtener el resultado", "error")


def cmd_list():
    """Comando: listar documentos"""
    try:
        response = requests.get(f"{BASE_URL}/documents", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if data["total"] == 0:
                print("No hay documentos procesados")
                return
            
            headers = ["ID", "Archivo", "Tipo", "Estado", "Fecha"]
            rows = []
            
            for doc in data["documents"]:
                rows.append([
                    doc["id"][:8] + "...",
                    doc["filename"],
                    doc.get("document_type", "N/A"),
                    doc["status"],
                    doc["uploaded_at"][:19]
                ])
            
            print_table(headers, rows, "Documentos Procesados")
            print(f"\nTotal: {data['total']} documentos")
        else:
            print_status("Error obteniendo lista", "error")
    except Exception as e:
        print_status(f"Error: {e}", "error")


def cmd_stats():
    """Comando: estadísticas"""
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            print("📊 Estadísticas del Sistema")
            print(f"Total de documentos: {data['total_documents']}")
            print(f"Tasa de éxito: {data['success_rate']:.2%}")
            
            # Distribución por estado
            if data["status_distribution"]:
                print("\nDistribución por Estado:")
                for status, count in data["status_distribution"].items():
                    print(f"   {status}: {count}")
            
            # Distribución por tipo
            if data["type_distribution"]:
                print("\nDistribución por Tipo:")
                for doc_type, count in data["type_distribution"].items():
                    print(f"   {doc_type}: {count}")
        else:
            print_status("Error obteniendo estadísticas", "error")
    except Exception as e:
        print_status(f"Error: {e}", "error")


def main():
    """Función principal CLI simple"""
    if len(sys.argv) < 2:
        print("DocN8NAgent CLI")
        print("Uso:")
        print("  python -m src.cli_simple status           - Verificar estado del servicio")
        print("  python -m src.cli_simple process <file>   - Procesar documento")
        print("  python -m src.cli_simple list             - Listar documentos")
        print("  python -m src.cli_simple stats            - Ver estadísticas")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        cmd_status()
    elif command == "process":
        if len(sys.argv) < 3:
            print_status("Especifica el archivo a procesar", "error")
            return
        file_path = sys.argv[2]
        actions = sys.argv[3:] if len(sys.argv) > 3 else None
        cmd_process(file_path, actions)
    elif command == "list":
        cmd_list()
    elif command == "stats":
        cmd_stats()
    else:
        print_status(f"Comando no reconocido: {command}", "error")


if __name__ == "__main__":
    main()
