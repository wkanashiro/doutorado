#!/usr/bin/env python3
"""
Script para analisar o conteúdo dos shapefiles dos talhões nas ortofotos da soja.
Mostra estrutura, atributos, geometrias e estatísticas dos shapefiles.
"""

import os
import geopandas as gpd
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import numpy as np

def analisar_shapefile(shapefile_path):
    """Analisa um shapefile e retorna informações detalhadas."""
    print(f"\n{'='*60}")
    print(f"ANALISANDO: {shapefile_path}")
    print(f"{'='*60}")
    
    try:
        # Carregar o shapefile
        gdf = gpd.read_file(shapefile_path)
        
        print(f"📊 INFORMAÇÕES GERAIS:")
        print(f"   • Número de feições: {len(gdf)}")
        print(f"   • Sistema de coordenadas: {gdf.crs}")
        print(f"   • Tipo de geometria: {gdf.geometry.geom_type.unique()}")
        print(f"   • Bounds: {gdf.total_bounds}")
        
        print(f"\n📋 COLUNAS/ATRIBUTOS:")
        for col in gdf.columns:
            if col != 'geometry':
                dtype = gdf[col].dtype
                unique_vals = gdf[col].nunique()
                print(f"   • {col} ({dtype}): {unique_vals} valores únicos")
                
                # Mostrar alguns valores se for string ou poucos valores únicos
                if dtype == 'object' or unique_vals <= 10:
                    sample_vals = gdf[col].unique()[:5]
                    print(f"     Exemplos: {sample_vals}")
        
        print(f"\n📐 GEOMETRIAS:")
        for idx, row in gdf.iterrows():
            geom = row.geometry
            if hasattr(geom, 'area'):
                area_ha = geom.area / 10000  # Converter para hectares (assumindo metros)
                print(f"   • Talhão {idx}: Área = {area_ha:.2f} ha, Perímetro = {geom.length:.2f} m")
            
            # Mostrar atributos importantes
            attrs = []
            for col in gdf.columns:
                if col != 'geometry' and pd.notna(row[col]):
                    attrs.append(f"{col}={row[col]}")
            if attrs:
                print(f"     Atributos: {', '.join(attrs[:3])}")  # Primeiros 3 atributos
        
        print(f"\n📈 ESTATÍSTICAS:")
        if 'area' in [col.lower() for col in gdf.columns]:
            area_col = [col for col in gdf.columns if col.lower() == 'area'][0]
            print(f"   • Área total: {gdf[area_col].sum():.2f}")
            print(f"   • Área média: {gdf[area_col].mean():.2f}")
            print(f"   • Área min/max: {gdf[area_col].min():.2f} / {gdf[area_col].max():.2f}")
        
        # Calcular área geométrica se não houver coluna de área
        areas_geom = [geom.area / 10000 for geom in gdf.geometry]  # em hectares
        print(f"   • Área geométrica total: {sum(areas_geom):.2f} ha")
        print(f"   • Área geométrica média: {np.mean(areas_geom):.2f} ha")
        
        return gdf
        
    except Exception as e:
        print(f"❌ Erro ao analisar shapefile: {e}")
        return None

def main():
    """Função principal para analisar todos os shapefiles."""
    base_dir = Path("/home/lades/computer_vision/wesley/mae-soja/ortofotos_soja")
    
    print("🔍 ANÁLISE DOS SHAPEFILES DOS TALHÕES")
    print("="*60)
    
    shapefile_paths = []
    
    # Buscar todos os shapefiles
    for area_dir in base_dir.iterdir():
        if area_dir.is_dir():
            for file in area_dir.iterdir():
                if file.suffix == '.shp' and 'TALHOES' in file.name.upper():
                    shapefile_paths.append(file)
    
    print(f"📁 Encontrados {len(shapefile_paths)} shapefiles de talhões:")
    for path in shapefile_paths:
        print(f"   • {path.parent.name}/{path.name}")
    
    # Analisar cada shapefile
    gdfs = []
    for shapefile_path in shapefile_paths:
        gdf = analisar_shapefile(shapefile_path)
        if gdf is not None:
            gdfs.append((shapefile_path.parent.name, gdf))
    
    # Resumo geral
    print(f"\n{'='*60}")
    print("📊 RESUMO GERAL")
    print(f"{'='*60}")
    
    total_talhoes = sum(len(gdf) for _, gdf in gdfs)
    total_areas = []
    
    for area_name, gdf in gdfs:
        areas = [geom.area / 10000 for geom in gdf.geometry]
        total_areas.extend(areas)
        print(f"   • {area_name}: {len(gdf)} talhões, {sum(areas):.2f} ha")
    
    print(f"\n🌾 ESTATÍSTICAS CONSOLIDADAS:")
    print(f"   • Total de áreas: {len(gdfs)}")
    print(f"   • Total de talhões: {total_talhoes}")
    print(f"   • Área total: {sum(total_areas):.2f} ha")
    print(f"   • Área média por talhão: {np.mean(total_areas):.2f} ha")
    print(f"   • Área min/max por talhão: {min(total_areas):.2f} / {max(total_areas):.2f} ha")

if __name__ == "__main__":
    main()
