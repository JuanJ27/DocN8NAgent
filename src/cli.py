"""
Cliente CLI para interactuar con DocN8NAgent
"""
import asyncio
import click
import requests
import json
from pathlib import Path
from typing import List

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
    from rich.json import JSON
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

try:
    import nest_asyncio
    nest_asyncio.apply()
except ImportError:
    pass

BASE_URL = "http://localhost:8000"


@click.group()
def cli():
    """DocN8NAgent - Cliente CLI para procesamiento de documentos"""
    pass


@cli.command()
def status():
    """Verifica el estado del servicio"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            console.print("✅ Servicio activo", style="green")
            console.print(f"Formatos soportados: {', '.join(data['supported_formats'])}")
        else:
            console.print("❌ Servicio no disponible", style="red")
    except Exception as e:
        console.print(f"❌ Error conectando al servicio: {e}", style="red")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--actions", "-a", multiple=True, 
              help="Acciones a realizar (classify, extract, validate, detect_fraud)")
def process(file_path: str, actions: List[str]):
    """Procesa un documento"""
    try:
        # Subir archivo
        with console.status("[bold green]Subiendo documento..."):
            with open(file_path, "rb") as f:
                files = {"file": (Path(file_path).name, f)}
                response = requests.post(f"{BASE_URL}/upload", files=files)
                
                if response.status_code != 200:
                    console.print(f"❌ Error subiendo archivo: {response.text}", style="red")
                    return
                
                upload_data = response.json()
                document_id = upload_data["document_id"]
                
        console.print(f"📄 Documento subido: {document_id}")
        
        # Procesar documento
        process_data = {}
        if actions:
            process_data["actions"] = list(actions)
            
        with console.status("[bold blue]Procesando documento..."):
            response = requests.post(
                f"{BASE_URL}/process/{document_id}",
                json=process_data
            )
            
            if response.status_code != 200:
                console.print(f"❌ Error procesando: {response.text}", style="red")
                return
        
        console.print("🔄 Procesamiento iniciado")
        
        # Esperar y mostrar resultado
        with Progress() as progress:
            task = progress.add_task("[cyan]Esperando resultado...", total=100)
            
            for i in range(100):
                await asyncio.sleep(0.1)
                progress.update(task, advance=1)
                
                # Verificar estado cada segundo
                if i % 10 == 0:
                    status_response = requests.get(f"{BASE_URL}/status/{document_id}")
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        if status_data["status"] in ["completed", "failed", "rejected"]:
                            break
        
        # Obtener resultado final
        result_response = requests.get(f"{BASE_URL}/result/{document_id}")
        if result_response.status_code == 200:
            result = result_response.json()
            display_result(result)
        else:
            console.print("❌ No se pudo obtener el resultado", style="red")
            
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@cli.command()
def list():
    """Lista todos los documentos"""
    try:
        response = requests.get(f"{BASE_URL}/documents")
        if response.status_code == 200:
            data = response.json()
            
            table = Table(title="Documentos Procesados")
            table.add_column("ID", style="cyan")
            table.add_column("Archivo", style="magenta")
            table.add_column("Tipo", style="green")
            table.add_column("Estado", style="yellow")
            table.add_column("Fecha", style="blue")
            
            for doc in data["documents"]:
                table.add_row(
                    doc["id"][:8] + "...",
                    doc["filename"],
                    doc.get("document_type", "N/A"),
                    doc["status"],
                    doc["uploaded_at"][:19]
                )
            
            console.print(table)
            console.print(f"Total: {data['total']} documentos")
        else:
            console.print("❌ Error obteniendo lista", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


@cli.command()
def stats():
    """Muestra estadísticas del sistema"""
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            
            console.print("📊 Estadísticas del Sistema", style="bold")
            console.print(f"Total de documentos: {data['total_documents']}")
            console.print(f"Tasa de éxito: {data['success_rate']:.2%}")
            
            # Distribución por estado
            table_status = Table(title="Distribución por Estado")
            table_status.add_column("Estado", style="cyan")
            table_status.add_column("Cantidad", style="magenta")
            
            for status, count in data["status_distribution"].items():
                table_status.add_row(status, str(count))
            
            console.print(table_status)
            
            # Distribución por tipo
            if data["type_distribution"]:
                table_type = Table(title="Distribución por Tipo")
                table_type.add_column("Tipo", style="green")
                table_type.add_column("Cantidad", style="yellow")
                
                for doc_type, count in data["type_distribution"].items():
                    table_type.add_row(doc_type, str(count))
                
                console.print(table_type)
            
        else:
            console.print("❌ Error obteniendo estadísticas", style="red")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")


def display_result(result: dict):
    """Muestra el resultado del procesamiento"""
    console.print("🎯 Resultado del Procesamiento", style="bold green")
    
    # Información del documento
    doc = result["document"]
    console.print(f"📄 Archivo: {doc['filename']}")
    console.print(f"🏷️  Estado: {doc['status']}")
    console.print(f"⏱️  Tiempo: {result.get('processing_time', 0):.2f}s")
    
    # Clasificación
    if result.get("classification"):
        classification = result["classification"]
        console.print(f"📂 Tipo: {classification['document_type']} (confianza: {classification['confidence']:.2%})")
    
    # Datos extraídos
    if result.get("extraction") and result["extraction"]["fields"]:
        console.print("📋 Datos Extraídos:", style="bold")
        for field, value in result["extraction"]["fields"].items():
            confidence = result["extraction"]["confidence_scores"].get(field, 0)
            console.print(f"  • {field}: {value} (confianza: {confidence:.2%})")
    
    # Validación
    if result.get("validation"):
        validation = result["validation"]
        status_icon = "✅" if validation["is_valid"] else "❌"
        console.print(f"{status_icon} Validación: {'Válido' if validation['is_valid'] else 'Inválido'}")
        console.print(f"📊 Puntuación de cumplimiento: {validation['compliance_score']:.2%}")
        
        if validation["errors"]:
            console.print("❌ Errores:", style="red")
            for error in validation["errors"]:
                console.print(f"  • {error}")
        
        if validation["warnings"]:
            console.print("⚠️  Advertencias:", style="yellow")
            for warning in validation["warnings"]:
                console.print(f"  • {warning}")
    
    # Detección de fraudes
    if result.get("fraud_detection"):
        fraud = result["fraud_detection"]
        fraud_icon = "🚨" if fraud["is_fraudulent"] else "🛡️"
        console.print(f"{fraud_icon} Fraude: {'Detectado' if fraud['is_fraudulent'] else 'No detectado'}")
        console.print(f"⚠️  Riesgo: {fraud['risk_score']:.2%}")
        
        if fraud["risk_factors"]:
            console.print("🔍 Factores de riesgo:")
            for factor in fraud["risk_factors"]:
                console.print(f"  • {factor}")


if __name__ == "__main__":
    # Permitir asyncio en funciones síncronas
    import nest_asyncio
    nest_asyncio.apply()
    cli()
