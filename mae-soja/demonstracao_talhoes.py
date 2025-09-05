#!/usr/bin/env python3
"""
Demonstração de como usar shapefiles de talhões para segmentação baseada em plots.
Este script mostra como integrar informações dos talhões com a segmentação das ortofotos.
"""

import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.features import geometry_mask
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

def criar_visualizacao_talhoes_ortofoto():
    """Cria uma visualização dos talhões sobrepostos na ortofoto."""
    
    print("📍 DEMONSTRAÇÃO: TALHÕES + ORTOFOTO")
    print("="*50)
    
    # Caminho para uma das áreas
    area_dir = Path("/home/lades/computer_vision/wesley/mae-soja/ortofotos_soja/Angelica - 198 - Figueira (Scatolin) - Gleba 04")
    
    # Arquivos principais
    shapefile_path = area_dir / "198_Figueira_Scatolin_04_08_01_25_Talhoes.shp"
    tif_files = list(area_dir.glob("*.tif"))
    
    if not tif_files:
        print("❌ Nenhum arquivo TIF encontrado na área")
        return
    
    ortofoto_path = tif_files[0]
    print(f"📂 Ortofoto: {ortofoto_path.name}")
    print(f"📂 Shapefile: {shapefile_path.name}")
    
    # Carregar shapefile
    gdf = gpd.read_file(shapefile_path)
    print(f"📊 {len(gdf)} talhões encontrados")
    
    # Carregar ortofoto
    with rasterio.open(ortofoto_path) as src:
        print(f"📏 Dimensões da ortofoto: {src.width} x {src.height}")
        print(f"📍 CRS da ortofoto: {src.crs}")
        print(f"📍 CRS dos talhões: {gdf.crs}")
        
        # Verificar se os sistemas de coordenadas são compatíveis
        if src.crs != gdf.crs:
            print("⚠️  Reprojetando talhões para o CRS da ortofoto...")
            gdf = gdf.to_crs(src.crs)
        
        # Ler uma porção da ortofoto para visualização
        print("📖 Lendo amostra da ortofoto (1/4 da resolução)...")
        data = src.read([1, 2, 3], 
                       out_shape=(3, src.height//4, src.width//4), 
                       resampling=rasterio.enums.Resampling.bilinear)
        
        # Ajustar transform para a resolução reduzida
        transform = src.transform * src.transform.scale(4, 4)
        
        # Criar máscara dos talhões
        print("🎭 Criando máscaras dos talhões...")
        masks = {}
        for idx, row in gdf.iterrows():
            geom = [row.geometry.__geo_interface__]
            try:
                mask_array = geometry_mask(geom, 
                                         out_shape=(src.height//4, src.width//4),
                                         transform=transform,
                                         invert=True)
                masks[idx] = mask_array
                area_pixels = np.sum(mask_array)
                print(f"   • Talhão {row.get('talhao', idx)}: {area_pixels} pixels, {row.get('area_ha', 'N/A')} ha")
            except Exception as e:
                print(f"   ❌ Erro no talhão {idx}: {e}")
    
    print(f"\n✅ Análise concluída! {len(masks)} máscaras de talhões criadas.")
    return gdf, masks, data

def demonstrar_segmentacao_por_talhao():
    """Demonstra como fazer segmentação específica por talhão."""
    
    print("\n🎯 DEMONSTRAÇÃO: SEGMENTAÇÃO POR TALHÃO")
    print("="*50)
    
    print("""
📋 CONCEITOS IMPORTANTES DOS SHAPEFILES:

1. 🗂️  ESTRUTURA DOS TALHÕES:
   • Cada talhão é um polígono georreferenciado
   • Contém metadados: fazenda, gleba, área, código único
   • Sistemas de coordenadas: EPSG:32722 ou EPSG:31982 (UTM)

2. 📊 ATRIBUTOS PRINCIPAIS:
   • cod_talhao: Código único do talhão
   • area_ha: Área em hectares
   • fazenda/propriedad: Nome da propriedade
   • gleba: Subdivisão da fazenda
   • talhao: Número do talhão
   • date_plots: Data de criação/atualização

3. 🎯 VANTAGENS PARA SEGMENTAÇÃO:
   • Análise específica por talhão (comparação entre áreas)
   • Cálculo de estatísticas por propriedade
   • Geração de relatórios por fazenda/gleba
   • Validação de resultados com áreas conhecidas

4. 🔄 FLUXO DE TRABALHO SUGERIDO:
   a) Carregar ortofoto e shapefile
   b) Verificar/ajustar sistemas de coordenadas
   c) Para cada talhão:
      - Extrair região da ortofoto (crop)
      - Aplicar segmentação na região
      - Calcular estatísticas (área por classe)
      - Salvar resultados com metadados do talhão
   d) Consolidar resultados por fazenda/gleba
    """)
    
    # Exemplo de estrutura de dados para resultados
    exemplo_resultado = {
        "fazenda": "FAZ. FIGUEIRA (SCATOLIN)",
        "gleba": 4,
        "talhao": 11,
        "codigo_talhao": "0001980000400011",
        "area_total_ha": 33.43,
        "resultados_segmentacao": {
            "solo_nu": {"area_ha": 5.2, "percentual": 15.5},
            "cultura": {"area_ha": 25.8, "percentual": 77.2},
            "plantas_daninhas": {"area_ha": 2.4, "percentual": 7.3}
        },
        "coordenadas": {
            "centroide": [-52.123456, -23.654321],
            "bounds": [182472.77, 7567756.15, 184956.56, 7569563.75]
        }
    }
    
    print("\n📄 EXEMPLO DE RESULTADO POR TALHÃO:")
    print(json.dumps(exemplo_resultado, indent=2, ensure_ascii=False))

def comparar_pipelines():
    """Compara o pipeline atual com o sistema avançado."""
    
    print("\n🔄 COMPARAÇÃO DE PIPELINES")
    print("="*50)
    
    print("""
🟢 PIPELINE ATUAL (ortofoto_inference.py):
  ✅ Segmentação de ortofoto inteira com sliding window
  ✅ Saída em GeoTIFF georreferenciado
  ✅ Mapa de cores e estatísticas globais
  ✅ Processamento simples e direto
  ❌ Não usa informações dos talhões
  ❌ Não gera relatórios por propriedade

🟡 SISTEMA AVANÇADO (prediction_orthophoto/):
  ✅ Processamento baseado em talhões
  ✅ Batch processing de múltiplas áreas
  ✅ Acumulação de probabilidades e descarte de bordas
  ✅ Saída em shapefile com atributos
  ✅ Relatórios detalhados por fazenda/gleba
  ❌ Mais complexo de usar e configurar
  ❌ Requer mais setup e dependências

🎯 INTEGRAÇÃO SUGERIDA:
  1. Manter simplicidade do pipeline atual
  2. Adicionar opção de processamento por talhão
  3. Gerar relatórios consolidados
  4. Preservar saídas tanto em raster quanto vetorial
    """)

def main():
    """Função principal de demonstração."""
    try:
        # Demonstrações
        criar_visualizacao_talhoes_ortofoto()
        demonstrar_segmentacao_por_talhao()
        comparar_pipelines()
        
        print("\n🎉 CONCLUSÃO")
        print("="*50)
        print("""
Os shapefiles dos talhões contêm informações valiosas para análise agrícola:

• 📍 Localização precisa de cada talhão (polígonos georreferenciados)
• 📊 Metadados: fazenda, gleba, área, códigos únicos
• 🎯 Possibilidade de análise específica por área de cultivo
• 📈 Geração de relatórios estruturados por propriedade

Próximos passos sugeridos:
1. Integrar processamento por talhão ao pipeline atual
2. Implementar geração de relatórios por fazenda/gleba  
3. Criar visualizações comparativas entre talhões
4. Validar resultados com dados de campo por talhão
        """)
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")

if __name__ == "__main__":
    main()
