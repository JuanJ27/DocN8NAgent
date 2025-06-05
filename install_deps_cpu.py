#!/usr/bin/env python3
"""
Script de instalación para DocN8NAgent optimizado para sistemas sin GPU
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, check=True, shell=False):
    """Ejecuta un comando y maneja errores"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {e}")
        return False


def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major != 3 or version.minor < 8:
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")


def install_system_dependencies():
    """Instala dependencias del sistema"""
    print("🔧 Instalando dependencias del sistema...")
    
    # Detectar distribución de Linux
    try:
        with open('/etc/os-release', 'r') as f:
            os_info = f.read().lower()
        
        if 'ubuntu' in os_info or 'debian' in os_info:
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y tesseract-ocr tesseract-ocr-spa",
                "sudo apt-get install -y libgl1-mesa-glx libglib2.0-0",  # Para OpenCV
                "sudo apt-get install -y poppler-utils",  # Para pdf2image
                "sudo apt-get install -y libmagic1"  # Para detección de tipos de archivo
            ]
        elif 'centos' in os_info or 'rhel' in os_info or 'fedora' in os_info:
            commands = [
                "sudo yum update -y",
                "sudo yum install -y tesseract tesseract-langpack-spa",
                "sudo yum install -y mesa-libGL glib2",
                "sudo yum install -y poppler-utils",
                "sudo yum install -y file"
            ]
        else:
            print("⚠️  Distribución no detectada automáticamente")
            print("   Por favor instala manualmente:")
            print("   - tesseract-ocr y tesseract-ocr-spa")
            print("   - poppler-utils")
            print("   - libgl1-mesa-glx")
            return True
        
        for cmd in commands:
            print(f"Ejecutando: {cmd}")
            if not run_command(cmd, shell=True):
                print(f"⚠️  Falló: {cmd}")
                return False
        
        print("✅ Dependencias del sistema instaladas")
        return True
        
    except Exception as e:
        print(f"⚠️  Error instalando dependencias del sistema: {e}")
        return False


def install_python_dependencies():
    """Instala dependencias de Python optimizadas para CPU"""
    print("📦 Instalando dependencias de Python (optimizadas para CPU)...")
    
    # Actualizar pip
    print("Actualizando pip...")
    if not run_command("python -m pip install --upgrade pip"):
        return False
    
    # Instalar PyTorch CPU first
    print("Instalando PyTorch CPU...")
    torch_cmd = "python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    if not run_command(torch_cmd, shell=True):
        print("⚠️  Error instalando PyTorch CPU, intentando versión estándar...")
        if not run_command("python -m pip install torch torchvision torchaudio"):
            return False
    
    # Instalar resto de dependencias
    print("Instalando otras dependencias...")
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        if not run_command(f"python -m pip install -r {requirements_file}"):
            print("⚠️  Error con requirements.txt, instalando dependencias esenciales...")
            essential_packages = [
                "transformers>=4.30.0",
                "sentence-transformers>=2.2.0",
                "fastapi>=0.100.0",
                "uvicorn>=0.23.0",
                "opencv-python-headless>=4.8.0",
                "pillow>=10.0.0",
                "pytesseract>=0.3.10",
                "easyocr>=1.7.0",
                "spacy>=3.6.0",
                "pandas>=2.0.0",
                "numpy>=1.24.0",
                "scikit-learn>=1.3.0",
                "loguru>=0.7.0",
                "click>=8.0.0",
                "rich>=13.0.0",
                "python-multipart>=0.0.6",
                "aiofiles>=23.0.0",
                "pydantic>=2.0.0",
                "pdf2image>=1.16.0",
                "python-docx>=0.8.11",
                "pypdf2>=3.0.0"
            ]
            
            for package in essential_packages:
                print(f"Instalando {package}...")
                if not run_command(f"python -m pip install {package}"):
                    print(f"⚠️  Falló: {package}")
    
    print("✅ Dependencias de Python instaladas")
    return True


def install_spacy_model():
    """Instala modelo de spaCy para español"""
    print("🔤 Instalando modelo de spaCy para español...")
    
    # Intentar instalar modelo pequeño primero
    if run_command("python -m spacy download es_core_news_sm", check=False):
        print("✅ Modelo es_core_news_sm instalado")
        return True
    
    # Si falla, intentar modelo más básico
    if run_command("python -m spacy download es_core_news_md", check=False):
        print("✅ Modelo es_core_news_md instalado")
        return True
    
    print("⚠️  No se pudo instalar modelo de spaCy, funcionará con funcionalidad limitada")
    return False


def download_nltk_data():
    """Descarga datos necesarios de NLTK"""
    print("📚 Descargando datos de NLTK...")
    
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        print("✅ Datos de NLTK descargados")
        return True
    except Exception as e:
        print(f"⚠️  Error descargando datos de NLTK: {e}")
        return False


def create_directories():
    """Crea directorios necesarios"""
    print("📁 Creando directorios...")
    
    directories = [
        "data/uploads",
        "data/examples", 
        "models",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")


def test_installation():
    """Prueba la instalación"""
    print("🧪 Probando instalación...")
    
    try:
        # Test imports básicos
        import torch
        print(f"✅ PyTorch {torch.__version__} (CPU: {not torch.cuda.is_available()})")
        
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
        
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
        
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
        
        # Test OCR
        import pytesseract
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract {version}")
        except:
            print("⚠️  Tesseract instalado pero no accesible")
        
        import easyocr
        print("✅ EasyOCR instalado")
        
        print("✅ Instalación exitosa!")
        return True
        
    except ImportError as e:
        print(f"❌ Error en importación: {e}")
        return False


def main():
    """Función principal"""
    print("🚀 Configurando DocN8NAgent para sistemas sin GPU")
    print("=" * 50)
    
    # Verificar Python
    check_python_version()
    
    # Crear directorios
    create_directories()
    
    # Instalar dependencias del sistema
    if not install_system_dependencies():
        print("⚠️  Algunas dependencias del sistema fallaron, continuando...")
    
    # Instalar dependencias de Python
    if not install_python_dependencies():
        print("❌ Error instalando dependencias de Python")
        sys.exit(1)
    
    # Instalar modelo de spaCy
    install_spacy_model()
    
    # Descargar datos de NLTK
    download_nltk_data()
    
    # Probar instalación
    if test_installation():
        print("\n" + "=" * 50)
        print("✅ ¡Instalación completada exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar demo: python demo.py")
        print("   2. Iniciar API: python -m src.api.main")
        print("   3. Usar CLI: python -m src.cli status")
    else:
        print("\n❌ La instalación tuvo problemas")
        print("   Revisa los errores arriba y intenta instalar manualmente")


if __name__ == "__main__":
    main()
