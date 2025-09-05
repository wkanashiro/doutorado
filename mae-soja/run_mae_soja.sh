#!/bin/bash
# Script de conveniência para execução dos processamentos principais.

# Diretório base do projeto
BASE_DIR="/home/lades/computer_vision/wesley/mae-soja"
SCRIPTS_DIR="$BASE_DIR/scripts/principais"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MAE-Soja: Processamento de Ortofotos Agrícolas${NC}"
echo -e "${BLUE}=================================================${NC}"

# Função para mostrar ajuda
show_help() {
    echo -e "${YELLOW}Uso:${NC}"
    echo "  $0 processar <area>     # Processar área específica"
    echo "  $0 processar all        # Processar todas as áreas"
    echo "  $0 estilos <area>       # Gerar estilos QGIS para área específica"
    echo "  $0 estilos all          # Gerar estilos QGIS para todas as áreas"
    echo "  $0 listar               # Listar áreas disponíveis"
    echo "  $0 status               # Verificar status do projeto"
    echo ""
    echo -e "${YELLOW}Exemplos:${NC}"
    echo "  $0 processar \"Ivinhema___230___Santista___Gleba_01\""
    echo "  $0 processar all"
    echo "  $0 estilos all"
}

# Função para listar áreas disponíveis
list_areas() {
    echo -e "${GREEN}📂 Áreas disponíveis:${NC}"
    if [ -d "$BASE_DIR/data/input/ortofotos_soja" ]; then
        ls -1 "$BASE_DIR/data/input/ortofotos_soja/"
    else
        echo -e "${RED}❌ Diretório de ortofotos não encontrado!${NC}"
    fi
}

# Função para verificar status
check_status() {
    echo -e "${GREEN}📊 Status do Projeto:${NC}"
    
    # Verificar modelo
    if [ -f "$BASE_DIR/models/modelo_final/iter_40000.pth" ]; then
        echo -e "  ✅ Modelo treinado: ${GREEN}OK${NC}"
    else
        echo -e "  ❌ Modelo treinado: ${RED}NÃO ENCONTRADO${NC}"
    fi
    
    # Verificar ambiente
    if [ -d "$BASE_DIR/env-mae" ]; then
        echo -e "  ✅ Ambiente virtual: ${GREEN}OK${NC}"
    else
        echo -e "  ❌ Ambiente virtual: ${RED}NÃO ENCONTRADO${NC}"
    fi
    
    # Verificar dados de entrada
    if [ -d "$BASE_DIR/data/input/ortofotos_soja" ]; then
        area_count=$(ls -1 "$BASE_DIR/data/input/ortofotos_soja" | wc -l)
        echo -e "  ✅ Ortofotos: ${GREEN}$area_count áreas${NC}"
    else
        echo -e "  ❌ Ortofotos: ${RED}NÃO ENCONTRADAS${NC}"
    fi
    
    # Verificar resultados
    if [ -d "$BASE_DIR/data/output/resultados_segmentacao_talhoes" ]; then
        result_count=$(ls -1 "$BASE_DIR/data/output/resultados_segmentacao_talhoes" 2>/dev/null | wc -l)
        echo -e "  ✅ Resultados: ${GREEN}$result_count áreas processadas${NC}"
    else
        echo -e "  ⚠️  Resultados: ${YELLOW}Nenhuma área processada ainda${NC}"
    fi
}

# Função para processar
process_area() {
    local area=$1
    echo -e "${GREEN}🔄 Processando ortofotos...${NC}"
    
    cd "$BASE_DIR"
    source env-mae/bin/activate
    
    if [ "$area" = "all" ]; then
        python "$SCRIPTS_DIR/generate_shapefiles.py" --all
    else
        python "$SCRIPTS_DIR/generate_shapefiles.py" --area "$area"
    fi
}

# Função para gerar estilos
generate_styles() {
    local area=$1
    echo -e "${GREEN}🎨 Gerando estilos QGIS...${NC}"
    
    cd "$BASE_DIR"
    source env-mae/bin/activate
    
    if [ "$area" = "all" ]; then
        python "$SCRIPTS_DIR/generate_qgis_styles.py"
    else
        python "$SCRIPTS_DIR/generate_qgis_styles.py" --area "$area"
    fi
}

# Parse dos argumentos
case "$1" in
    "processar")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Especifique uma área ou 'all'${NC}"
            show_help
            exit 1
        fi
        process_area "$2"
        ;;
    "estilos")
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Especifique uma área ou 'all'${NC}"
            show_help
            exit 1
        fi
        generate_styles "$2"
        ;;
    "listar")
        list_areas
        ;;
    "status")
        check_status
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Comando inválido: $1${NC}"
        show_help
        exit 1
        ;;
esac
