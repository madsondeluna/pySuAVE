#!/bin/bash
# Script para limpar arquivos de metadados do macOS
# Útil para volumes externos

echo "🧹 Limpando arquivos de metadados do macOS..."

# Remover arquivos ._*
echo "Removendo arquivos ._* ..."
find . -name "._*" -type f -delete

# Remover .DS_Store
echo "Removendo .DS_Store ..."
find . -name ".DS_Store" -type f -delete

echo "✅ Limpeza concluída!"
echo ""
echo "Para evitar que esses arquivos sejam criados novamente, execute:"
echo "  defaults write com.apple.desktopservices DSDontWriteNetworkStores -bool true"
echo "  defaults write com.apple.desktopservices DSDontWriteUSBStores -bool true"
