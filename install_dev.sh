#!/bin/bash
# Script de instalacao do ambiente de desenvolvimento pySuAVE

echo "========================================="
echo "Instalacao do ambiente pySuAVE"
echo "========================================="
echo ""

# Verificar Python
echo "1. Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python 3 nao encontrado. Instale Python 3.9 ou superior."
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "   $PYTHON_VERSION encontrado"
echo ""

# Criar ambiente virtual
echo "2. Criando ambiente virtual..."
if [ -d "venv" ]; then
    echo "   Ambiente virtual ja existe. Removendo..."
    rm -rf venv
fi

python3 -m venv venv
echo "   Ambiente virtual criado"
echo ""

# Ativar ambiente virtual
echo "3. Ativando ambiente virtual..."
source venv/bin/activate
echo "   Ambiente ativado"
echo ""

# Atualizar pip
echo "4. Atualizando pip..."
pip install --upgrade pip --quiet
echo "   pip atualizado"
echo ""

# Instalar dependencias
echo "5. Instalando dependencias..."
pip install -e ".[dev]" --quiet
echo "   Dependencias instaladas"
echo ""

# Executar testes
echo "6. Executando testes..."
echo ""
pytest tests/ -v

echo ""
echo "========================================="
echo "Instalacao concluida!"
echo "========================================="
echo ""
echo "Para ativar o ambiente virtual:"
echo "  source venv/bin/activate"
echo ""
echo "Para executar testes:"
echo "  pytest tests/ -v"
echo ""
echo "Para executar exemplo:"
echo "  python examples/example_basic_io.py"
echo ""
