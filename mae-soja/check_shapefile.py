#!/usr/bin/env python3
"""
Script para verificar o conteúdo do shapefile de resultados.
"""

import geopandas as gpd
import pandas as pd
import sys

def main():
    try:
        # Caminho para o shapefile
        shp_path = '/home/lades/computer_vision/wesley/mae-soja/resultados_segmentacao_talhoes/Ivinhema___230___Santista___Gleba_01/Ivinhema___230___Santista___Gleba_01_resultados.shp'
        
        # Carregar shapefile
        gdf = gpd.read_file(shp_path)
        
        print("📊 ANÁLISE DO SHAPEFILE DE RESULTADOS")
        print("="*60)
        
        print(f"Total de registros: {len(gdf)}")
        print(f"Colunas disponíveis: {list(gdf.columns)}")
        print()
        
        # Verificar se as colunas de resultado existem
        result_columns = ['dom_class', 'dom_perc', 'bg_perc', 'gram_alto', 'gram_baixo', 'folh_larga', 'trepadeira']
        available_result_cols = [col for col in result_columns if col in gdf.columns]
        
        print(f"Colunas de resultado disponíveis: {available_result_cols}")
        print()
        
        if available_result_cols:
            print("📈 ESTATÍSTICAS DOS RESULTADOS:")
            print("-" * 40)
            
            # Mostrar dados para cada talhão
            for idx, row in gdf.iterrows():
                print(f"Talhão {idx}:")
                if 'dom_class' in gdf.columns:
                    print(f"  Classe dominante: {row.get('dom_class', 'N/A')} ({row.get('dom_perc', 0):.1f}%)")
                
                # Mostrar percentuais de cada classe
                for col in ['bg_perc', 'gram_alto', 'gram_baixo', 'folh_larga', 'trepadeira']:
                    if col in gdf.columns:
                        value = row.get(col, 0)
                        if value > 0:
                            class_name = {
                                'bg_perc': 'Background',
                                'gram_alto': 'Graminea Porte Alto',
                                'gram_baixo': 'Graminea Porte Baixo', 
                                'folh_larga': 'Outras Folhas Largas',
                                'trepadeira': 'Trepadeira'
                            }[col]
                            print(f"  - {class_name}: {value:.1f}%")
                print()
            
            # Resumo de distribuição de classes dominantes
            if 'dom_class' in gdf.columns:
                print("🎯 DISTRIBUIÇÃO DE CLASSES DOMINANTES:")
                print("-" * 40)
                class_counts = gdf['dom_class'].value_counts()
                for class_name, count in class_counts.items():
                    percentage = (count / len(gdf)) * 100
                    print(f"{class_name}: {count} talhões ({percentage:.1f}%)")
        else:
            print("❌ Nenhuma coluna de resultado encontrada no shapefile!")
            print("Colunas disponíveis:", list(gdf.columns))
            
    except Exception as e:
        print(f"❌ Erro ao analisar shapefile: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
