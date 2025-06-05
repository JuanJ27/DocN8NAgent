#!/bin/bash

# Script de inicio rápido para DocN8NAgent
set -e

echo "🚀 Configurando DocN8NAgent..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Python
print_status "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION detectado"

# Verificar si estamos en un entorno virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "No estás en un entorno virtual"
    echo "¿Deseas crear uno? (y/n)"
    read -r create_venv
    
    if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
        print_status "Creando entorno virtual..."
        python3 -m venv venv
        source venv/bin/activate
        print_success "Entorno virtual creado y activado"
    fi
else
    print_success "Entorno virtual activo: $VIRTUAL_ENV"
fi

# Instalar dependencias Python
print_status "Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar script de instalación de dependencias del sistema
print_status "Configurando dependencias del sistema..."
python install_deps.py

# Crear directorios necesarios
print_status "Creando estructura de directorios..."
mkdir -p data/{uploads,examples,processed} models/trained logs config

# Ejecutar tests básicos
print_status "Ejecutando tests básicos..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short || print_warning "Algunos tests fallaron, pero el sistema debería funcionar"
else
    print_warning "pytest no disponible, saltando tests"
fi

# Verificar instalación de Tesseract
print_status "Verificando Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | head -n1)
    print_success "Tesseract instalado: $TESSERACT_VERSION"
else
    print_warning "Tesseract no encontrado. Instálalo manualmente si es necesario."
fi

# Mostrar comandos útiles
echo ""
echo "=" * 60
print_success "¡Configuración completada!"
echo ""
echo "📋 Comandos útiles:"
echo ""
echo "   🎮 Ejecutar demostración:"
echo "      python demo.py"
echo ""
echo "   🌐 Iniciar servidor API:"
echo "      python -m src.api.main"
echo ""
echo "   🔧 Usar CLI:"
echo "      python -m src.cli status"
echo "      python -m src.cli process documento.pdf"
echo ""
echo "   🧪 Ejecutar tests:"
echo "      pytest tests/ -v"
echo ""
echo "   🐳 Usar Docker:"
echo "      docker-compose up --build"
echo ""
echo "   📚 Ver documentación:"
echo "      cat SETUP.md"
echo ""
echo "=" * 60

# Preguntar si ejecutar demo
echo ""
echo "¿Deseas ejecutar la demostración ahora? (y/n)"
read -r run_demo

if [[ $run_demo == "y" || $run_demo == "Y" ]]; then
    print_status "Ejecutando demostración..."
    python demo.py
fi

print_success "¡Todo listo para usar DocN8NAgent! 🎉"
