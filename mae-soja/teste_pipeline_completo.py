#!/usr/bin/env python3
"""
Teste completo do pipeline de segmentação por talhões.
Processa uma área pequena para validar todos os outputs.
"""

import os
import sys
import cv2
import numpy as np
import torch
import geopandas as gpd
from rasterio import features
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds
import json
from pathlib import Path
import time

def load_model():
    """Carrega o modelo de segmentação."""
    try:
        # Adiciona o path do mmsegmentation
        mmseg_path = "/home/lades/computer_vision/wesley/mae-soja/mmsegmentation"
        if mmseg_path not in sys.path:
            sys.path.insert(0, mmseg_path)
        
        from mmseg.apis import inference_model, init_model
        
        # Caminhos do modelo
        config_file = '/home/lades/computer_vision/wesley/mae-soja/output_mae_soja-prof-wesley-17062025_200-epochs_mmsegmentation_5classes-40000iterations/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
        checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/output_mae_soja-prof-wesley-17062025_200-epochs_mmsegmentation_5classes-40000iterations/iter_40000.pth'
        
        print("Carregando modelo...")
        model = init_model(config_file, checkpoint_file, device='cuda:0')
        print("Modelo carregado com sucesso!")
        return model
        
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        return None

def get_smallest_area():
    """Encontra a área com menor número de talhões para teste rápido."""
    base_path = "/home/lades/computer_vision/wesley/mae-soja/ortofotos_soja"
    areas = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    
    min_talhoes = float('inf')
    smallest_area = None
    
    for area in areas:
        area_path = os.path.join(base_path, area)
        shp_files = [f for f in os.listdir(area_path) if f.endswith('.shp')]
        
        if shp_files:
            shp_path = os.path.join(area_path, shp_files[0])
            try:
                gdf = gpd.read_file(shp_path)
                num_talhoes = len(gdf)
                print(f"Área {area}: {num_talhoes} talhões")
                
                if num_talhoes < min_talhoes:
                    min_talhoes = num_talhoes
                    smallest_area = area
            except Exception as e:
                print(f"Erro ao ler shapefile de {area}: {e}")
    
    return smallest_area, min_talhoes

def process_single_plot(model, ortofoto_path, plot_geometry, plot_info, output_dir):
    """Processa um único talhão."""
    print(f"Processando talhão {plot_info.get('talhao', 'N/A')}...")
    
    # Lê a ortofoto
    with rasterio.open(ortofoto_path) as src:
        # Obtém bounds do talhão em coordenadas da imagem
        minx, miny, maxx, maxy = plot_geometry.bounds
        
        # Converte coordenadas geográficas para coordenadas de pixel
        window = rasterio.windows.from_bounds(minx, miny, maxx, maxy, src.transform)
        
        # Lê apenas a região do talhão
        plot_data = src.read(window=window)
        plot_transform = src.window_transform(window)
        
        # Transpõe para formato HWC (Height, Width, Channels)
        if plot_data.shape[0] == 3:  # Se for RGB
            plot_image = np.transpose(plot_data, (1, 2, 0))
        else:
            plot_image = plot_data[0]  # Se for grayscale
    
    # Redimensiona para o tamanho esperado pelo modelo (256x256)
    target_size = 256
    if len(plot_image.shape) == 3:
        plot_image = cv2.resize(plot_image, (target_size, target_size))
    else:
        plot_image = cv2.resize(plot_image, (target_size, target_size))
    print(f"Imagem redimensionada para {target_size}x{target_size}")
    
    # Segmentação
    try:
        from mmseg.apis import inference_model
        result = inference_model(model, plot_image)
        pred_mask = result.pred_sem_seg.data.cpu().numpy()[0]
        print(f"Segmentação concluída. Shape: {pred_mask.shape}")
    except Exception as e:
        print(f"Erro na segmentação: {e}")
        return None
    
    # Calcula estatísticas
    unique_classes, counts = np.unique(pred_mask, return_counts=True)
    total_pixels = pred_mask.size
    
    stats = {
        'talhao': plot_info.get('talhao', 'N/A'),
        'area_m2': plot_info.get('area', 0),
        'total_pixels': int(total_pixels),
        'classes': {}
    }
    
    class_names = ['Background', 'Soja', 'Buva', 'Capim_Amargoso', 'Other_Weeds']
    
    for class_id, count in zip(unique_classes, counts):
        if class_id < len(class_names):
            percentage = (count / total_pixels) * 100
            stats['classes'][class_names[class_id]] = {
                'pixels': int(count),
                'percentage': float(percentage)
            }
    
    # Salva resultados
    talhao_id = plot_info.get('talhao', f'plot_{len(os.listdir(output_dir))}')
    
    # Salva máscara como PNG
    mask_path = os.path.join(output_dir, f'talhao_{talhao_id}_mask.png')
    cv2.imwrite(mask_path, pred_mask.astype(np.uint8) * 50)  # Multiplica por 50 para visualização
    
    # Salva estatísticas JSON
    stats_path = os.path.join(output_dir, f'talhao_{talhao_id}_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Resultados salvos: {mask_path}, {stats_path}")
    return stats

def main():
    """Função principal de teste."""
    print("=== TESTE COMPLETO DO PIPELINE ===")
    
    # Encontra a área menor para teste
    area_name, num_talhoes = get_smallest_area()
    if not area_name:
        print("Nenhuma área encontrada!")
        return
    
    print(f"Testando com área: {area_name} ({num_talhoes} talhões)")
    
    # Caminhos
    area_path = f"/home/lades/computer_vision/wesley/mae-soja/ortofotos_soja/{area_name}"
    output_dir = "/home/lades/computer_vision/wesley/mae-soja/teste_pipeline_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Encontra arquivos
    tif_files = [f for f in os.listdir(area_path) if f.endswith('.tif')]
    shp_files = [f for f in os.listdir(area_path) if f.endswith('.shp')]
    
    if not tif_files or not shp_files:
        print("Arquivos TIF ou SHP não encontrados!")
        return
    
    ortofoto_path = os.path.join(area_path, tif_files[0])
    shapefile_path = os.path.join(area_path, shp_files[0])
    
    print(f"Ortofoto: {tif_files[0]}")
    print(f"Shapefile: {shp_files[0]}")
    
    # Carrega modelo
    model = load_model()
    if model is None:
        print("Falha ao carregar o modelo!")
        return
    
    # Lê shapefile
    try:
        gdf = gpd.read_file(shapefile_path)
        print(f"Shapefile carregado: {len(gdf)} talhões")
        print(f"Colunas: {list(gdf.columns)}")
    except Exception as e:
        print(f"Erro ao ler shapefile: {e}")
        return
    
    # Processa apenas os primeiros 2 talhões para teste rápido
    test_plots = gdf.head(2) if len(gdf) > 2 else gdf
    
    all_stats = []
    start_time = time.time()
    
    for idx, row in test_plots.iterrows():
        plot_info = row.to_dict()
        plot_geometry = row.geometry
        
        stats = process_single_plot(model, ortofoto_path, plot_geometry, plot_info, output_dir)
        if stats:
            all_stats.append(stats)
    
    # Salva resumo geral
    summary = {
        'area': area_name,
        'total_plots_processed': len(all_stats),
        'processing_time_seconds': time.time() - start_time,
        'plots': all_stats
    }
    
    summary_path = os.path.join(output_dir, 'summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n=== TESTE CONCLUÍDO ===")
    print(f"Processados {len(all_stats)} talhões em {summary['processing_time_seconds']:.1f}s")
    print(f"Resultados em: {output_dir}")
    print(f"Arquivos gerados:")
    for file in os.listdir(output_dir):
        print(f"  - {file}")

if __name__ == "__main__":
    main()
