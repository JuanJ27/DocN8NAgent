#!/bin/bash
# Script de inicio rápido para DocN8NAgent optimizado para CPU

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Iniciando DocN8NAgent (CPU optimizado)${NC}"
echo "=================================================="

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado. Creando...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar instalación
if ! python -c "import torch, transformers, fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Dependencias no instaladas. Instalando...${NC}"
    python install_deps_cpu.py
fi

echo -e "${GREEN}✅ Sistema listo${NC}"
echo ""
echo "Opciones disponibles:"
echo "  1. Ejecutar demo:        python demo.py"
echo "  2. Iniciar servidor API: python -m src.api.main"
echo "  3. Usar CLI:            python -m src.cli_simple status"
echo ""

# Si se pasa un argumento, ejecutarlo
if [ "$1" = "demo" ]; then
    echo -e "${BLUE}📋 Ejecutando demostración...${NC}"
    python demo.py
elif [ "$1" = "api" ]; then
    echo -e "${BLUE}🌐 Iniciando servidor API...${NC}"
    echo "Servidor disponible en: http://localhost:8000"
    echo "Documentación API: http://localhost:8000/docs"
    python -m src.api.main
elif [ "$1" = "cli" ]; then
    echo -e "${BLUE}💻 Iniciando CLI...${NC}"
    python -m src.cli_simple "$@"
else
    echo "Para ejecutar automáticamente:"
    echo "  ./quick_start.sh demo  # Ejecutar demostración"
    echo "  ./quick_start.sh api   # Iniciar servidor API"
    echo "  ./quick_start.sh cli   # Usar CLI"
fi
