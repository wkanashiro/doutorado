#!/usr/bin/env python3
"""
Script completo para processamento de ortofotos com segmentação por talhões.
Gera shapefiles e GeoTIFFs compatíveis com QGIS.
"""

import os
import sys
import cv2
import numpy as np
import torch
import geopandas as gpd
import rasterio
from rasterio.crs import CRS
from rasterio.transform import from_bounds
from rasterio.features import rasterize
from rasterio.mask import mask
import json
from pathlib import Path
import time
from tqdm import tqdm
import argparse
from shapely.geometry import mapping
import traceback

def load_model():
    """Carrega o modelo de segmentação."""
    try:
        # Adiciona o path do mmsegmentation
        mmseg_path = "/home/lades/computer_vision/wesley/mae-soja/mmsegmentation"
        if mmseg_path not in sys.path:
            sys.path.insert(0, mmseg_path)
        
        from mmseg.apis import inference_model, init_model
        
        # Caminhos do modelo
        config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
        checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
        
        print("Carregando modelo de segmentação...")
        model = init_model(config_file, checkpoint_file, device='cuda:0')
        
        # Colocar modelo em modo de avaliação
        model.eval()
        
        print("✓ Modelo carregado com sucesso!")
        print(f"✓ Modelo em modo de avaliação: {not model.training}")
        
        return model
        
    except Exception as e:
        print(f"✗ Erro ao carregar o modelo: {e}")
        return None

def process_single_plot(model, ortofoto_path, plot_geometry, plot_info, output_dir):
    """Processa um único talhão usando sliding window."""
    talhao_id = plot_info.get('FID', f"plot_{plot_info.get('index', 'unknown')}")
    print(f"  Processando talhão: {talhao_id}")
    
    # Lê a ortofoto
    with rasterio.open(ortofoto_path) as src:
        # Máscara da geometria do talhão
        geom = [mapping(plot_geometry)]
        try:
            masked_data, masked_transform = mask(src, geom, crop=True, filled=False)
            masked_crs = src.crs
        except Exception as e:
            print(f"    ✗ Erro ao extrair região do talhão: {e}")
            return None
        
        # Converte para formato de imagem (mantém resolução original)
        if masked_data.shape[0] == 3:  # RGB
            plot_image = np.transpose(masked_data, (1, 2, 0))
        else:
            plot_image = masked_data[0]
        
        # Remove valores NoData se existirem
        if hasattr(masked_data, 'mask'):
            valid_mask = ~masked_data.mask[0] if len(masked_data.mask.shape) > 2 else ~masked_data.mask
            if len(plot_image.shape) == 3:
                plot_image = np.where(np.stack([valid_mask]*3, axis=-1), plot_image, 0)
            else:
                plot_image = np.where(valid_mask, plot_image, 0)
               
    # Dimensões da imagem do talhão (resolução original)
    original_height, original_width = plot_image.shape[:2]
    print(f"    - Tamanho do talhão: {original_width}x{original_height}")
    
    # Parâmetros do sliding window
    tile_size = 256
    overlap = 64  # Overlap para evitar artefatos nas bordas
    
    # Aplica sliding window para segmentação
    pred_mask = apply_sliding_window_segmentation(model, plot_image, tile_size, overlap, output_dir, talhao_id)
    
    if pred_mask is None:
        print(f"    ✗ Falha na segmentação do talhão")
        return None
    
    print(f"    ✓ Segmentação concluída. Shape: {pred_mask.shape}")
    
    # Calcula estatísticas
    unique_classes, counts = np.unique(pred_mask, return_counts=True)
    total_pixels = pred_mask.size
    
    # Classes de daninhas (excluindo background)
    weed_classes = {
        1: 'Graminea Porte Alto',
        2: 'Graminea Porte Baixo',
        3: 'Outras Folhas Largas', 
        4: 'Trepadeira'
    }
    
    print(f"    - Classes detectadas: {unique_classes}")
    
    # Calcula estatísticas apenas para daninhas
    weed_stats = {}
    total_weed_pixels = 0
    dominant_weed_class = None
    dominant_weed_percentage = 0.0
    
    for class_id, count in zip(unique_classes, counts):
        if class_id in weed_classes:  # Apenas daninhas
            percentage = (count / total_pixels) * 100
            class_name = weed_classes[class_id]
            total_weed_pixels += count
            
            weed_stats[class_name] = {
                'class_id': int(class_id),
                'pixels': int(count),
                'percentage': float(percentage)
            }
            
            if percentage > dominant_weed_percentage:
                dominant_weed_percentage = percentage
                dominant_weed_class = class_name
    
    # Calcula cobertura total de daninhas
    weed_coverage = (total_weed_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0
    
    stats = {
        'talhao': str(talhao_id),
        'area_m2': float(plot_info.get('Area (km2)', 0)) * 1e6,
        'classe': plot_info.get('Classe', 'N/A'),
        'total_pixels': int(total_pixels),
        'weed_pixels': int(total_weed_pixels),
        'weed_coverage_percentage': float(weed_coverage),
        'weed_classes': weed_stats,
        'dominant_weed_class': dominant_weed_class,
        'dominant_weed_percentage': float(dominant_weed_percentage),
        'has_weeds': len(weed_stats) > 0
    }
    
    # Salva GeoTIFF da máscara
    geotiff_path = os.path.join(output_dir, f'talhao_{talhao_id}_segmentation.tif')
    with rasterio.open(
        geotiff_path, 'w',
        driver='GTiff',
        height=pred_mask.shape[0],
        width=pred_mask.shape[1],
        count=1,
        dtype=pred_mask.dtype,
        crs=masked_crs,
        transform=masked_transform,
        compress='lzw'
    ) as dst:
        dst.write(pred_mask, 1)
    
    # Salva estatísticas JSON
    stats_path = os.path.join(output_dir, f'talhao_{talhao_id}_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Adiciona estatísticas à geometria para o shapefile (apenas se houver daninhas)
    plot_info_enhanced = plot_info.copy()
    
    if stats['has_weeds']:
        plot_info_enhanced.update({
            'has_weeds': 'YES',
            'weed_cover': round(stats['weed_coverage_percentage'], 2),
            'dom_weed': stats['dominant_weed_class'][:10] if stats['dominant_weed_class'] else '',
            'dom_w_perc': round(stats['dominant_weed_percentage'], 2),
            'gram_alto': round(stats['weed_classes'].get('Graminea Porte Alto', {}).get('percentage', 0), 2),
            'gram_baixo': round(stats['weed_classes'].get('Graminea Porte Baixo', {}).get('percentage', 0), 2),
            'folh_larga': round(stats['weed_classes'].get('Outras Folhas Largas', {}).get('percentage', 0), 2),
            'trepadeira': round(stats['weed_classes'].get('Trepadeira', {}).get('percentage', 0), 2),
            'geotiff': os.path.basename(geotiff_path)
        })
        print(f"    ✓ Daninhas detectadas: {stats['weed_coverage_percentage']:.1f}% de cobertura")
        if stats['dominant_weed_class']:
            print(f"    ✓ Daninha dominante: {stats['dominant_weed_class']} ({stats['dominant_weed_percentage']:.1f}%)")
    else:
        plot_info_enhanced.update({
            'has_weeds': 'NO',
            'weed_cover': 0.0,
            'dom_weed': '',
            'dom_w_perc': 0.0,
            'gram_alto': 0.0,
            'gram_baixo': 0.0,
            'folh_larga': 0.0,
            'trepadeira': 0.0,
            'geotiff': os.path.basename(geotiff_path)
        })
        print(f"    ✓ Nenhuma daninha detectada (100% Background)")
    
    return plot_info_enhanced, stats
    
    # Calcula estatísticas
    unique_classes, counts = np.unique(pred_mask, return_counts=True)
    total_pixels = pred_mask.size
    
    # Mapeamento de classes conforme definido em daninhas.py
    class_names = {
        1: 'Graminea Porte Alto',
        2: 'Graminea Porte Baixo', 
        3: 'Outras Folhas Largas',
        4: 'Trepadeira'
    }
    
    # Classes de daninhas (excluindo background)
    weed_classes = {
        1: 'Graminea Porte Alto',
        2: 'Graminea Porte Baixo',
        3: 'Outras Folhas Largas', 
        4: 'Trepadeira'
    }
    
    print(f"    - Classes detectadas: {unique_classes}")
    
    # Calcula estatísticas apenas para daninhas
    weed_stats = {}
    total_weed_pixels = 0
    dominant_weed_class = None
    dominant_weed_percentage = 0.0
    
    for class_id, count in zip(unique_classes, counts):
        if class_id in weed_classes:  # Apenas daninhas
            percentage = (count / total_pixels) * 100
            class_name = weed_classes[class_id]
            total_weed_pixels += count
            
            weed_stats[class_name] = {
                'class_id': int(class_id),
                'pixels': int(count),
                'percentage': float(percentage)
            }
            
            if percentage > dominant_weed_percentage:
                dominant_weed_percentage = percentage
                dominant_weed_class = class_name
    
    # Calcula cobertura total de daninhas
    weed_coverage = (total_weed_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0
    
    stats = {
        'talhao': str(talhao_id),
        'area_m2': float(plot_info.get('Area (km2)', 0)) * 1e6,
        'classe': plot_info.get('Classe', 'N/A'),
        'total_pixels': int(total_pixels),
        'weed_pixels': int(total_weed_pixels),
        'weed_coverage_percentage': float(weed_coverage),
        'weed_classes': weed_stats,
        'dominant_weed_class': dominant_weed_class,
        'dominant_weed_percentage': float(dominant_weed_percentage),
        'has_weeds': len(weed_stats) > 0
    }
    
    # Salva GeoTIFF da máscara
    geotiff_path = os.path.join(output_dir, f'talhao_{talhao_id}_segmentation.tif')
    with rasterio.open(
        geotiff_path, 'w',
        driver='GTiff',
        height=pred_mask.shape[0],
        width=pred_mask.shape[1],
        count=1,
        dtype=pred_mask.dtype,
        crs=masked_crs,
        transform=masked_transform,
        compress='lzw'
    ) as dst:
        dst.write(pred_mask, 1)
    
    # Salva estatísticas JSON
    stats_path = os.path.join(output_dir, f'talhao_{talhao_id}_stats.json')
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Adiciona estatísticas à geometria para o shapefile (apenas se houver daninhas)
    plot_info_enhanced = plot_info.copy()
    
    if stats['has_weeds']:
        plot_info_enhanced.update({
            'has_weeds': 'YES',
            'weed_cover': round(stats['weed_coverage_percentage'], 2),
            'dom_weed': stats['dominant_weed_class'][:10] if stats['dominant_weed_class'] else '',
            'dom_w_perc': round(stats['dominant_weed_percentage'], 2),
            'gram_alto': round(stats['weed_classes'].get('Graminea Porte Alto', {}).get('percentage', 0), 2),
            'gram_baixo': round(stats['weed_classes'].get('Graminea Porte Baixo', {}).get('percentage', 0), 2),
            'folh_larga': round(stats['weed_classes'].get('Outras Folhas Largas', {}).get('percentage', 0), 2),
            'trepadeira': round(stats['weed_classes'].get('Trepadeira', {}).get('percentage', 0), 2),
            'geotiff': os.path.basename(geotiff_path)
        })
        print(f"    ✓ Daninhas detectadas: {stats['weed_coverage_percentage']:.1f}% de cobertura")
        if stats['dominant_weed_class']:
            print(f"    ✓ Daninha dominante: {stats['dominant_weed_class']} ({stats['dominant_weed_percentage']:.1f}%)")
    else:
        plot_info_enhanced.update({
            'has_weeds': 'NO',
            'weed_cover': 0.0,
            'dom_weed': '',
            'dom_w_perc': 0.0,
            'gram_alto': 0.0,
            'gram_baixo': 0.0,
            'folh_larga': 0.0,
            'trepadeira': 0.0,
            'geotiff': os.path.basename(geotiff_path)
        })
        print(f"    ✓ Nenhuma daninha detectada (100% Background)")
    
    return plot_info_enhanced, stats

def process_area(area_path, output_base_dir):
    """Processa uma área completa (ortofoto + shapefile)."""
    area_name = os.path.basename(area_path)
    print(f"\n{'='*60}")
    print(f"PROCESSANDO ÁREA: {area_name}")
    print(f"{'='*60}")
    
    # Encontra arquivos
    tif_files = [f for f in os.listdir(area_path) if f.endswith('.tif')]
    shp_files = [f for f in os.listdir(area_path) if f.endswith('.shp')]
    
    if not tif_files or not shp_files:
        print(f"✗ Arquivos TIF ou SHP não encontrados em {area_path}")
        return None
    
    ortofoto_path = os.path.join(area_path, tif_files[0])
    shapefile_path = os.path.join(area_path, shp_files[0])
    
    print(f"📄 Ortofoto: {tif_files[0]}")
    print(f"📍 Shapefile: {shp_files[0]}")
    
    # Cria diretório de saída
    safe_area_name = area_name.replace(' ', '_').replace('/', '_').replace('-', '_')
    output_dir = os.path.join(output_base_dir, safe_area_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # Carrega modelo
    model = load_model()
    if model is None:
        print("✗ Falha ao carregar o modelo!")
        return None
    
    # Lê shapefile
    try:
        gdf = gpd.read_file(shapefile_path)
        print(f"📊 Shapefile carregado: {len(gdf)} talhões")
        print(f"📋 Colunas: {list(gdf.columns)}")
    except Exception as e:
        print(f"✗ Erro ao ler shapefile: {e}")
        return None
    
    # Processa cada talhão
    all_stats = []
    enhanced_plots = []
    
    start_time = time.time()
    
    for idx, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Processando talhões"):
        plot_info = row.to_dict()
        plot_info['index'] = idx  # Adiciona índice
        plot_geometry = row.geometry
        
        result = process_single_plot(model, ortofoto_path, plot_geometry, plot_info, output_dir)
        if result:
            enhanced_info, stats = result
            enhanced_plots.append(enhanced_info)
            all_stats.append(stats)
    
    # Cria shapefile com resultados (FORA do loop)
    if enhanced_plots:
        try:
            results_gdf = gdf.copy()
            
            # Adiciona colunas de resultados focadas em daninhas
            new_columns = {
                'has_weeds': 'NO',
                'weed_cover': 0.0,
                'dom_weed': '',
                'dom_w_perc': 0.0,
                'gram_alto': 0.0,
                'gram_baixo': 0.0,
                'folh_larga': 0.0,
                'trepadeira': 0.0,
                'geotiff': ''
            }
            
            for col_name, default_value in new_columns.items():
                if col_name not in results_gdf.columns:
                    results_gdf[col_name] = default_value
            
            # Preenche dados
            for i, enhanced_info in enumerate(enhanced_plots):
                if i < len(results_gdf):
                    for key, value in enhanced_info.items():
                        if key != 'geometry' and key in results_gdf.columns:
                            results_gdf.loc[results_gdf.index[i], key] = value
            
            # Salva shapefile de resultados
            results_shp_path = os.path.join(output_dir, f'{safe_area_name}_resultados.shp')
            results_gdf.to_file(results_shp_path)
            print(f"📁 Shapefile de resultados salvo: {results_shp_path}")
            
        except Exception as e:
            print(f"⚠️  Erro ao salvar shapefile: {e}")
            traceback.print_exc()
    
    # Salva resumo geral
    summary = {
        'area': area_name,
        'ortofoto': tif_files[0],
        'shapefile': shp_files[0],
        'total_plots': len(gdf),
        'processed_plots': len(all_stats),
        'processing_time_seconds': time.time() - start_time,
        'output_directory': output_dir,
        'class_summary': {},
        'plots': all_stats
    }
    
    # Resumo por daninhas
    weed_counts = {}
    plots_with_weeds = 0
    total_weed_coverage = 0.0
    
    for stats in all_stats:
        if stats['has_weeds']:
            plots_with_weeds += 1
            total_weed_coverage += stats['weed_coverage_percentage']
            
            # Conta ocorrências de cada tipo de daninha
            for weed_class, weed_data in stats['weed_classes'].items():
                if weed_data['percentage'] > 0:  # Apenas se detectada
                    weed_counts[weed_class] = weed_counts.get(weed_class, 0) + 1
    
    avg_weed_coverage = total_weed_coverage / plots_with_weeds if plots_with_weeds > 0 else 0.0
    
    summary['weed_summary'] = {
        'plots_with_weeds': plots_with_weeds,
        'plots_without_weeds': len(all_stats) - plots_with_weeds,
        'weed_infestation_rate': (plots_with_weeds / len(all_stats) * 100) if all_stats else 0.0,
        'average_weed_coverage': avg_weed_coverage,
        'weed_types_detected': weed_counts
    }
    
    summary['class_summary'] = weed_counts  # Manter compatibilidade
    
    summary_path = os.path.join(output_dir, 'summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 RESUMO DA ÁREA: {area_name}")
    print(f"⏱️  Tempo de processamento: {summary['processing_time_seconds']:.1f}s")
    print(f"📈 Talhões processados: {len(all_stats)}/{len(gdf)}")
    print(f"📂 Resultados salvos em: {output_dir}")
    
    print(f"\n� ANÁLISE DE DANINHAS:")
    print(f"   📊 Talhões com daninhas: {plots_with_weeds}/{len(all_stats)} ({(plots_with_weeds/len(all_stats)*100):.1f}%)")
    print(f"   📊 Talhões sem daninhas: {len(all_stats) - plots_with_weeds}/{len(all_stats)} ({((len(all_stats) - plots_with_weeds)/len(all_stats)*100):.1f}%)")
    if plots_with_weeds > 0:
        print(f"   📊 Cobertura média de daninhas: {avg_weed_coverage:.1f}%")
    
    print("\n🎯 Tipos de daninhas detectadas:")
    if weed_counts:
        for weed_type, count in weed_counts.items():
            percentage = (count / len(all_stats)) * 100 if all_stats else 0
            print(f"   {weed_type}: {count} talhões ({percentage:.1f}%)")
    else:
        print("   Nenhuma daninha detectada em nenhum talhão")
    
    return summary

def apply_sliding_window_segmentation(model, image, tile_size=256, overlap=64, output_dir=None, talhao_id=None):
    """
    Aplica segmentação usando sliding window mantendo a resolução original.
    
    Args:
        model: Modelo de segmentação carregado
        image: Imagem do talhão (numpy array HWC)
        tile_size: Tamanho dos tiles (padrão 256x256)
        overlap: Sobreposição entre tiles
        output_dir: Diretório para salvar debug
        talhao_id: ID do talhão para debug
        
    Returns:
        numpy array: Máscara de segmentação na resolução original
    """
    try:
        # Adiciona o path do mmsegmentation
        mmseg_path = "/home/lades/computer_vision/wesley/mae-soja/mmsegmentation"
        if mmseg_path not in sys.path:
            sys.path.insert(0, mmseg_path)
            
        from mmseg.apis import inference_model
        
        height, width = image.shape[:2]
        
        # Inicializa a máscara de resultado com zeros
        result_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Calcula step baseado no overlap
        step = tile_size - overlap
        
        # Calcula posições dos tiles
        x_positions = list(range(0, width, step))
        y_positions = list(range(0, height, step))
        
        # Adiciona posições finais se necessário
        if x_positions[-1] + tile_size < width:
            x_positions.append(width - tile_size)
        if y_positions[-1] + tile_size < height:
            y_positions.append(height - tile_size)
        
        total_tiles = len(x_positions) * len(y_positions)
        print(f"    - Processando {total_tiles} tiles de {tile_size}x{tile_size} com overlap de {overlap}")
        
        # Contador de tiles processados
        tile_count = 0
        
        # Processa cada tile
        for y in y_positions:
            for x in x_positions:
                tile_count += 1
                
                # Define limites do tile
                y_end = min(y + tile_size, height)
                x_end = min(x + tile_size, width)
                
                # Extrai o tile
                tile = image[y:y_end, x:x_end]
                
                # Faz padding se necessário para completar 256x256
                if tile.shape[0] < tile_size or tile.shape[1] < tile_size:
                    padded_tile = np.zeros((tile_size, tile_size, 3), dtype=np.uint8)
                    padded_tile[:tile.shape[0], :tile.shape[1]] = tile
                    tile = padded_tile
                
                # Realiza inferência no tile
                with torch.no_grad():
                    result = inference_model(model, tile)
                    tile_mask = result.pred_sem_seg.data.cpu().numpy()[0]
                
                # Recorta a parte válida (sem padding)
                valid_h = y_end - y
                valid_w = x_end - x
                valid_mask = tile_mask[:valid_h, :valid_w]
                
                # Atualiza a máscara resultado
                # Para overlaps, usa a média das predições ou a classe majoritária
                if overlap > 0:
                    # Para simplificar, vamos usar a última predição (pode ser melhorado)
                    result_mask[y:y_end, x:x_end] = valid_mask
                else:
                    result_mask[y:y_end, x:x_end] = valid_mask
                
                # Progress report
                if tile_count % 10 == 0 or tile_count == total_tiles:
                    print(f"    - Processados {tile_count}/{total_tiles} tiles")
        
        # Salva uma amostra de tile para debug
        if output_dir and talhao_id and total_tiles > 0:
            # Salva o primeiro tile como exemplo
            first_tile = image[:min(tile_size, height), :min(tile_size, width)]
            debug_tile_path = os.path.join(output_dir, f'talhao_{talhao_id}_sample_tile.png')
            cv2.imwrite(debug_tile_path, cv2.cvtColor(first_tile, cv2.COLOR_RGB2BGR))
        
        # Estatísticas finais
        unique_classes, counts = np.unique(result_mask, return_counts=True)
        print(f"    ✓ Sliding window concluído. Classes detectadas: {dict(zip(unique_classes, counts))}")
        
        return result_mask
        
    except Exception as e:
        print(f"    ✗ Erro no sliding window: {e}")
        traceback.print_exc()
        return np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Processa ortofotos com segmentação por talhões')
    parser.add_argument('--area', type=str, help='Nome da área específica para processar')
    parser.add_argument('--all', action='store_true', help='Processa todas as áreas')
    parser.add_argument('--output', type=str, default='/home/lades/computer_vision/wesley/mae-soja/data/output/resultados_segmentacao_talhoes',
                       help='Diretório base de saída')
    
    args = parser.parse_args()
    
    base_path = "/home/lades/computer_vision/wesley/mae-soja/data/input/ortofotos_soja"
    
    if not os.path.exists(base_path):
        print(f"❌ Diretório base não encontrado: {base_path}")
        return
    
    areas = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    
    if not areas:
        print(f"❌ Nenhuma área encontrada em: {base_path}")
        return
    
    os.makedirs(args.output, exist_ok=True)
    
    if args.area:
        # Processa área específica
        if args.area in areas:
            area_path = os.path.join(base_path, args.area)
            process_area(area_path, args.output)
        else:
            print(f"❌ Área '{args.area}' não encontrada. Áreas disponíveis:")
            for area in areas:
                print(f"  - {area}")
    
    elif args.all:
        # Processa todas as áreas
        print(f"🚀 INICIANDO PROCESSAMENTO DE TODAS AS ÁREAS")
        print(f"📂 Total de áreas encontradas: {len(areas)}")
        
        all_summaries = []
        total_start_time = time.time()
        
        for area in areas:
            area_path = os.path.join(base_path, area)
            summary = process_area(area_path, args.output)
            if summary:
                all_summaries.append(summary)
        
        # Resumo geral
        total_time = time.time() - total_start_time
        general_summary = {
            'total_areas': len(areas),
            'processed_areas': len(all_summaries),
            'total_processing_time_seconds': total_time,
            'areas': all_summaries
        }
        
        general_summary_path = os.path.join(args.output, 'resumo_geral.json')
        with open(general_summary_path, 'w', encoding='utf-8') as f:
            json.dump(general_summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 PROCESSAMENTO COMPLETO!")
        print(f"⏱️  Tempo total: {total_time:.1f}s")
        print(f"📊 Áreas processadas: {len(all_summaries)}/{len(areas)}")
        print(f"📁 Resumo geral salvo em: {general_summary_path}")
    
    else:
        # Lista áreas disponíveis
        print("📋 Áreas disponíveis para processamento:")
        for i, area in enumerate(areas, 1):
            print(f"  {i:2d}. {area}")
        
        print(f"\nUso:")
        print(f"  Processar área específica: python {sys.argv[0]} --area 'nome_da_area'")
        print(f"  Processar todas as áreas: python {sys.argv[0]} --all")

if __name__ == "__main__":
    main()