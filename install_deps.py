"""
Script para instalar dependencias adicionales del sistema
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Ejecuta un comando y maneja errores"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e.stderr}")
        return False


def install_tesseract():
    """Instala Tesseract OCR según el SO"""
    print("📋 Instalando Tesseract OCR...")
    
    # Detectar sistema operativo
    if sys.platform.startswith('linux'):
        # Ubuntu/Debian
        if os.path.exists('/usr/bin/apt-get'):
            commands = [
                "sudo apt-get update",
                "sudo apt-get install -y tesseract-ocr tesseract-ocr-spa",
                "sudo apt-get install -y libtesseract-dev"
            ]
        # CentOS/RHEL/Fedora
        elif os.path.exists('/usr/bin/yum'):
            commands = [
                "sudo yum install -y tesseract tesseract-langpack-spa"
            ]
        elif os.path.exists('/usr/bin/dnf'):
            commands = [
                "sudo dnf install -y tesseract tesseract-langpack-spa"
            ]
        else:
            print("❌ Distribución Linux no soportada. Instala Tesseract manualmente.")
            return False
            
    elif sys.platform == 'darwin':  # macOS
        commands = [
            "brew install tesseract tesseract-lang"
        ]
        
    elif sys.platform.startswith('win'):  # Windows
        print("⚠️  Para Windows, descarga Tesseract desde:")
        print("   https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Y añade el directorio de instalación al PATH")
        return True
        
    else:
        print(f"❌ Sistema operativo {sys.platform} no soportado")
        return False
    
    # Ejecutar comandos
    for command in commands:
        if not run_command(command, f"Ejecutando: {command}"):
            return False
    
    return True


def install_spacy_models():
    """Instala modelos de spaCy"""
    models = [
        ("es_core_news_sm", "Modelo español pequeño"),
        ("en_core_web_sm", "Modelo inglés pequeño")
    ]
    
    for model, description in models:
        command = f"python -m spacy download {model}"
        run_command(command, f"Instalando {description}")


def install_python_dependencies():
    """Instala dependencias adicionales de Python"""
    additional_deps = [
        "python-docx",
        "pdf2image", 
        "nest-asyncio",
        "rich",
        "click"
    ]
    
    for dep in additional_deps:
        command = f"pip install {dep}"
        run_command(command, f"Instalando {dep}")


def setup_directories():
    """Crea directorios necesarios"""
    directories = [
        "data/uploads",
        "data/examples", 
        "data/processed",
        "models/trained",
        "logs",
        "config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio creado: {directory}")


def create_example_config():
    """Crea archivo de configuración de ejemplo"""
    config_content = """
# Configuración de ejemplo para DocN8NAgent

# OCR Settings
OCR_LANGUAGE=spa
OCR_CONFIDENCE_THRESHOLD=0.7

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=True

# Processing Settings
MAX_FILE_SIZE=50MB
SUPPORTED_FORMATS=pdf,png,jpg,jpeg,tiff,docx

# Model Settings
USE_GPU=False
MODEL_CACHE_DIR=./models
"""
    
    with open("config/settings.env", "w") as f:
        f.write(config_content.strip())
    
    print("📄 Archivo de configuración creado: config/settings.env")


def main():
    """Función principal de instalación"""
    print("🚀 Configurando entorno DocN8NAgent")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} detectado")
    
    # Instalar dependencias del sistema
    install_tesseract()
    
    # Instalar dependencias Python adicionales
    install_python_dependencies()
    
    # Instalar modelos de spaCy
    install_spacy_models()
    
    # Configurar directorios
    setup_directories()
    
    # Crear configuración
    create_example_config()
    
    print("\n" + "=" * 50)
    print("✅ Instalación completada")
    print("\n📋 Próximos pasos:")
    print("1. Activa el entorno virtual si no lo has hecho:")
    print("   source venv/bin/activate")
    print("2. Ejecuta la demostración:")
    print("   python demo.py")
    print("3. Inicia el servidor API:")
    print("   python -m src.api.main")
    print("4. Prueba el CLI:")
    print("   python -m src.cli status")


if __name__ == "__main__":
    main()
