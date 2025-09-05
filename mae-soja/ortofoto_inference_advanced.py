#!/usr/bin/env python3
"""
Script avançado para inferência em ortofotos TIF usando sliding window
Pipeline MAE + MMSegmentation para segmentação semântica com suporte a talhões

Novidades desta versão:
- Processamento por talhões usando shapefiles
- Saídas compatíveis com QGIS (GeoTIFF + Shapefile)
- Relatórios JSON com estatísticas por talhão
- Arquivos de estilo QGIS (.qml)
- Processamento global ou por talhão

Exemplos de uso:

1. Processamento global (ortofoto completa):
   python ortofoto_inference_advanced.py --mode global --ortophoto /caminho/ortofoto.tif

2. Processamento por talhões:
   python ortofoto_inference_advanced.py --mode plots --ortophoto /caminho/ortofoto.tif --shapefile /caminho/talhoes.shp

3. Auto-detectar arquivos na pasta:
   python ortofoto_inference_advanced.py --mode auto --area-dir /caminho/pasta_area

4. Uso programático:
   from ortofoto_inference_advanced import process_with_plots
   results = process_with_plots('/caminho/ortofoto.tif', '/caminho/talhoes.shp')
"""

import rasterio
from rasterio.mask import mask
from rasterio.features import geometry_mask, rasterize
import numpy as np
import cv2
from tqdm import tqdm
import torch
import torch.nn.functional as F
from mmseg.apis import init_model, inference_model
import os
import matplotlib.pyplot as plt
from PIL import Image
import sys
import argparse
import geopandas as gpd
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configurações do modelo (podem ser alteradas se necessário)
DEFAULT_CHECKPOINT = '/home/lades/computer_vision/wesley/mae-soja/output_mae_soja-prof-wesley-17062025_200-epochs_mmsegmentation_5classes-40000iterations/iter_40000.pth'
DEFAULT_CONFIG = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation/configs/mae/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'

# Mapa de cores e nomes das classes
CLASS_NAMES = {
    0: 'Background',
    1: 'Gramínea Porte Alto', 
    2: 'Gramínea Porte Baixo',
    3: 'Outras Folhas Largas',
    4: 'Trepadeira'
}

COLOR_MAP = {
    0: [120, 120, 120], # Background - cinza
    1: [255, 0, 0],     # Gramínea Porte Alto - vermelho
    2: [0, 255, 0],     # Gramínea Porte Baixo - verde
    3: [0, 0, 255],     # Outras Folhas Largas - azul
    4: [0, 255, 255],   # Trepadeira - ciano
}

def find_files_in_area(area_dir):
    """
    Busca automaticamente ortofoto e shapefile em uma pasta de área.
    
    Args:
        area_dir (str): Caminho para a pasta da área
        
    Returns:
        tuple: (ortofoto_path, shapefile_path) ou (None, None) se não encontrar
    """
    area_path = Path(area_dir)
    
    # Buscar arquivos TIF (ortofoto)
    tif_files = list(area_path.glob("*.tif")) + list(area_path.glob("*.TIF"))
    
    # Buscar shapefiles de talhões
    shp_files = [f for f in area_path.glob("*.shp") if 'talhao' in f.name.lower() or 'talhoes' in f.name.lower()]
    
    ortofoto_path = tif_files[0] if tif_files else None
    shapefile_path = shp_files[0] if shp_files else None
    
    return ortofoto_path, shapefile_path

def load_and_validate_shapefile(shapefile_path, ortofoto_crs):
    """
    Carrega e valida shapefile, reprojetando se necessário.
    
    Args:
        shapefile_path (str): Caminho para o shapefile
        ortofoto_crs: CRS da ortofoto
        
    Returns:
        GeoDataFrame: Shapefile carregado e validado
    """
    print(f"📂 Carregando shapefile: {shapefile_path}")
    
    gdf = gpd.read_file(shapefile_path)
    print(f"   • {len(gdf)} talhões encontrados")
    print(f"   • CRS original: {gdf.crs}")
    
    # Reprojetar se necessário
    if gdf.crs != ortofoto_crs:
        print(f"   • Reprojetando para: {ortofoto_crs}")
        gdf = gdf.to_crs(ortofoto_crs)
    
    # Validar geometrias
    invalid_geoms = ~gdf.geometry.is_valid
    if invalid_geoms.any():
        print(f"   ⚠️  {invalid_geoms.sum()} geometrias inválidas encontradas, corrigindo...")
        gdf.loc[invalid_geoms, 'geometry'] = gdf.loc[invalid_geoms, 'geometry'].buffer(0)
    
    return gdf

def process_single_tile(model, tile, tile_size=256):
    """
    Processa um único tile com o modelo de segmentação.
    
    Args:
        model: Modelo carregado
        tile: Tile de imagem (numpy array)
        tile_size: Tamanho esperado do tile
        
    Returns:
        numpy array: Máscara de segmentação
    """
    # Pad se necessário
    if tile.shape[0] < tile_size or tile.shape[1] < tile_size:
        padded_tile = np.zeros((tile_size, tile_size, 3), dtype=np.uint8)
        padded_tile[:tile.shape[0], :tile.shape[1]] = tile
        tile = padded_tile
    
    # Fazer inferência
    result = inference_model(model, tile)
    pred_mask = result.pred_sem_seg.data.cpu().numpy()
    
    return pred_mask

def segment_region_with_sliding_window(model, image_data, tile_size=256, overlap=32):
    """
    Aplica segmentação usando sliding window em uma região da imagem.
    
    Args:
        model: Modelo carregado
        image_data: Dados da imagem (numpy array HWC)
        tile_size: Tamanho dos tiles
        overlap: Overlap entre tiles
        
    Returns:
        numpy array: Máscara de segmentação
    """
    height, width = image_data.shape[:2]
    segmentation_mask = np.zeros((height, width), dtype=np.uint8)
    
    # Calcular posições dos tiles
    step = tile_size - overlap
    x_positions = list(range(0, width - tile_size + 1, step))
    y_positions = list(range(0, height - tile_size + 1, step))
    
    # Adicionar tiles nas bordas se necessário
    if x_positions and x_positions[-1] + tile_size < width:
        x_positions.append(width - tile_size)
    if y_positions and y_positions[-1] + tile_size < height:
        y_positions.append(height - tile_size)
    
    total_tiles = len(x_positions) * len(y_positions)
    
    if total_tiles == 0:
        # Região muito pequena, processar como um único tile
        pred_mask = process_single_tile(model, image_data, tile_size)
        return pred_mask[:height, :width]
    
    # Processar tiles
    with tqdm(total=total_tiles, desc="  Processando tiles", leave=False) as pbar:
        for y in y_positions:
            for x in x_positions:
                # Extrair tile
                y_end = min(y + tile_size, height)
                x_end = min(x + tile_size, width)
                
                tile = image_data[y:y_end, x:x_end]
                
                # Processar tile
                pred_mask = process_single_tile(model, tile, tile_size)
                
                # Calcular região efetiva (sem padding)
                eff_h = y_end - y
                eff_w = x_end - x
                
                # Atualizar máscara de segmentação
                pred_resized = pred_mask[:eff_h, :eff_w]
                segmentation_mask[y:y_end, x:x_end] = pred_resized
                
                pbar.update(1)
    
    return segmentation_mask

def calculate_area_statistics(segmentation_mask, pixel_area_m2, class_names=None):
    """
    Calcula estatísticas de área por classe.
    
    Args:
        segmentation_mask: Máscara de segmentação
        pixel_area_m2: Área de cada pixel em metros quadrados
        class_names: Dicionário com nomes das classes
        
    Returns:
        dict: Estatísticas por classe
    """
    if class_names is None:
        class_names = CLASS_NAMES
    
    unique_classes, counts = np.unique(segmentation_mask, return_counts=True)
    total_pixels = segmentation_mask.size
    
    statistics = {}
    for class_id, count in zip(unique_classes, counts):
        area_m2 = count * pixel_area_m2
        area_ha = area_m2 / 10000  # Converter para hectares
        percentage = (count / total_pixels) * 100
        
        class_name = class_names.get(class_id, f'Classe {class_id}')
        
        statistics[class_name] = {
            'class_id': int(class_id),
            'pixels': int(count),
            'area_m2': float(area_m2),
            'area_ha': float(area_ha),
            'percentage': float(percentage)
        }
    
    return statistics

def process_with_plots(ortofoto_path, shapefile_path, output_dir=None, 
                      checkpoint_path=DEFAULT_CHECKPOINT, config_path=DEFAULT_CONFIG,
                      tile_size=256, overlap=32, device='cuda' if torch.cuda.is_available() else 'cpu'):
    """
    Processa ortofoto usando informações dos talhões.
    
    Args:
        ortofoto_path (str): Caminho para a ortofoto
        shapefile_path (str): Caminho para o shapefile dos talhões
        output_dir (str): Diretório de saída
        checkpoint_path (str): Caminho para o checkpoint do modelo
        config_path (str): Caminho para a configuração do modelo
        tile_size (int): Tamanho dos tiles
        overlap (int): Overlap entre tiles
        device (str): Dispositivo para inferência
        
    Returns:
        dict: Resultados do processamento
    """
    
    print("🎯 PROCESSAMENTO POR TALHÕES")
    print("="*50)
    
    # Configurar diretório de saída
    if output_dir is None:
        output_dir = Path(ortofoto_path).parent / "resultados_talhoes"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Carregar modelo
    print("🤖 Carregando modelo...")
    model = init_model(config_path, checkpoint_path, device=device)
    
    # Abrir ortofoto
    with rasterio.open(ortofoto_path) as src:
        print(f"📍 Ortofoto: {Path(ortofoto_path).name}")
        print(f"   • Dimensões: {src.width} x {src.height}")
        print(f"   • CRS: {src.crs}")
        
        # Calcular área do pixel em metros quadrados
        transform = src.transform
        pixel_area_m2 = abs(transform.a * transform.e)
        print(f"   • Área do pixel: {pixel_area_m2:.6f} m²")
        
        # Carregar shapefile
        gdf = load_and_validate_shapefile(shapefile_path, src.crs)
        
        # Ler dados da ortofoto
        if src.count >= 3:
            image_data = src.read([1, 2, 3])
            image_data = np.transpose(image_data, (1, 2, 0))  # HWC
        else:
            raise ValueError("A ortofoto deve ter pelo menos 3 canais (RGB)")
        
        # Normalizar para 0-255 se necessário
        if image_data.dtype != np.uint8:
            image_data = ((image_data - image_data.min()) / (image_data.max() - image_data.min()) * 255).astype(np.uint8)
        
        # Inicializar máscaras de resultado
        full_segmentation = np.zeros((src.height, src.width), dtype=np.uint8)
        plots_mask = np.zeros((src.height, src.width), dtype=np.uint8)
        
        # Processar cada talhão
        results = {
            'metadata': {
                'ortofoto': str(ortofoto_path),
                'shapefile': str(shapefile_path),
                'processamento': datetime.now().isoformat(),
                'total_talhoes': len(gdf),
                'pixel_area_m2': pixel_area_m2,
                'crs': str(src.crs)
            },
            'talhoes': {}
        }
        
        print(f"\n🌾 Processando {len(gdf)} talhões...")
        
        for idx, row in tqdm(gdf.iterrows(), total=len(gdf), desc="Talhões"):
            try:
                # Extrair informações do talhão
                talhao_info = {
                    'index': idx,
                }
                
                # Tentar extrair atributos comuns
                for col in gdf.columns:
                    if col != 'geometry':
                        value = row[col]
                        if pd.notna(value):
                            # Converter tipos não serializáveis
                            if hasattr(value, 'item'):  # numpy types
                                value = value.item()
                            elif hasattr(value, 'isoformat'):  # datetime
                                value = value.isoformat()
                            elif isinstance(value, (pd.Timestamp, datetime)):
                                value = str(value)
                            else:
                                value = str(value)  # Fallback para string
                            talhao_info[col] = value
                
                # Criar máscara do talhão
                geom = [row.geometry.__geo_interface__]
                
                # Mascarar a ortofoto para este talhão
                try:
                    masked_data, masked_transform = mask(src, geom, crop=True)
                    if masked_data.size == 0:
                        print(f"   ⚠️  Talhão {idx}: Região vazia após crop")
                        continue
                        
                    # Converter para HWC
                    if len(masked_data.shape) == 3:
                        masked_image = np.transpose(masked_data[:3], (1, 2, 0))
                    else:
                        print(f"   ⚠️  Talhão {idx}: Formato de dados inesperado")
                        continue
                    
                    # Normalizar se necessário
                    if masked_image.dtype != np.uint8:
                        valid_mask = masked_image.sum(axis=2) > 0
                        if valid_mask.any():
                            masked_image = ((masked_image - masked_image.min()) / (masked_image.max() - masked_image.min()) * 255).astype(np.uint8)
                    
                    # Aplicar segmentação
                    talhao_segmentation = segment_region_with_sliding_window(
                        model, masked_image, tile_size, overlap
                    )
                    
                    # Calcular estatísticas
                    stats = calculate_area_statistics(talhao_segmentation, pixel_area_m2)
                    talhao_info['estatisticas'] = stats
                    
                    # Salvar máscara do talhão individual
                    talhao_output_path = output_dir / f"talhao_{idx:03d}_segmentacao.tif"
                    with rasterio.open(
                        talhao_output_path,
                        'w',
                        driver='GTiff',
                        height=talhao_segmentation.shape[0],
                        width=talhao_segmentation.shape[1],
                        count=1,
                        dtype=talhao_segmentation.dtype,
                        crs=src.crs,
                        transform=masked_transform,
                        compress='lzw'
                    ) as dst:
                        dst.write(talhao_segmentation, 1)
                    
                    # Atualizar máscara global (rasterizar de volta)
                    full_geom_mask = geometry_mask(geom, 
                                                  out_shape=(src.height, src.width),
                                                  transform=src.transform,
                                                  invert=True)
                    plots_mask[full_geom_mask] = idx + 1  # ID do talhão
                    
                    print(f"   ✅ Talhão {idx}: {talhao_segmentation.shape[0]}x{talhao_segmentation.shape[1]} pixels processados")
                    
                except Exception as e:
                    print(f"   ❌ Erro no talhão {idx}: {e}")
                    continue
                
                results['talhoes'][f'talhao_{idx:03d}'] = talhao_info
                
            except Exception as e:
                print(f"   ❌ Erro geral no talhão {idx}: {e}")
                continue
        
        # Salvar máscara de IDs dos talhões
        plots_id_path = output_dir / "talhoes_ids.tif"
        with rasterio.open(
            plots_id_path,
            'w',
            driver='GTiff',
            height=src.height,
            width=src.width,
            count=1,
            dtype=plots_mask.dtype,
            crs=src.crs,
            transform=src.transform,
            compress='lzw'
        ) as dst:
            dst.write(plots_mask, 1)
        
        # Salvar resultados em JSON
        results_json_path = output_dir / "resultados_talhoes.json"
        with open(results_json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Criar shapefile com resultados
        create_results_shapefile(gdf, results, output_dir / "talhoes_resultados.shp")
        
        print(f"\n✅ Processamento por talhões concluído!")
        print(f"📁 Resultados salvos em: {output_dir}")
        print(f"   • Máscaras individuais: talhao_XXX_segmentacao.tif")
        print(f"   • IDs dos talhões: talhoes_ids.tif")
        print(f"   • Estatísticas: resultados_talhoes.json")
        print(f"   • Shapefile: talhoes_resultados.shp")
        
        return results

def create_results_shapefile(gdf, results, output_path):
    """
    Cria shapefile com os resultados da segmentação.
    
    Args:
        gdf: GeoDataFrame original
        results: Resultados do processamento
        output_path: Caminho para salvar o shapefile
    """
    # Criar nova GeoDataFrame com resultados
    results_gdf = gdf.copy()
    
    # Adicionar colunas de estatísticas
    for class_name in CLASS_NAMES.values():
        results_gdf[f'{class_name.replace(" ", "_")}_ha'] = 0.0
        results_gdf[f'{class_name.replace(" ", "_")}_pct'] = 0.0
    
    # Preencher dados
    for idx, row in results_gdf.iterrows():
        talhao_key = f'talhao_{idx:03d}'
        if talhao_key in results['talhoes']:
            stats = results['talhoes'][talhao_key].get('estatisticas', {})
            for class_name, data in stats.items():
                col_ha = f'{class_name.replace(" ", "_")}_ha'
                col_pct = f'{class_name.replace(" ", "_")}_pct'
                if col_ha in results_gdf.columns:
                    results_gdf.loc[idx, col_ha] = data['area_ha']
                    results_gdf.loc[idx, col_pct] = data['percentage']
    
    # Salvar shapefile
    results_gdf.to_file(output_path)
    print(f"   • Shapefile de resultados: {output_path}")

def process_global(ortofoto_path, output_dir=None,
                  checkpoint_path=DEFAULT_CHECKPOINT, config_path=DEFAULT_CONFIG,
                  tile_size=256, overlap=32, device='cuda' if torch.cuda.is_available() else 'cpu'):
    """
    Processa ortofoto completa (modo global original).
    
    Args:
        ortofoto_path (str): Caminho para a ortofoto
        output_dir (str): Diretório de saída
        checkpoint_path (str): Caminho para o checkpoint do modelo
        config_path (str): Caminho para a configuração do modelo
        tile_size (int): Tamanho dos tiles
        overlap (int): Overlap entre tiles
        device (str): Dispositivo para inferência
        
    Returns:
        dict: Resultados do processamento
    """
    
    print("🌍 PROCESSAMENTO GLOBAL")
    print("="*50)
    
    # Configurar diretório de saída
    if output_dir is None:
        output_dir = Path(ortofoto_path).parent / "resultados_global"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True)
    
    # Carregar modelo
    print("🤖 Carregando modelo...")
    model = init_model(config_path, checkpoint_path, device=device)
    
    # Processar ortofoto
    with rasterio.open(ortofoto_path) as src:
        print(f"📍 Ortofoto: {Path(ortofoto_path).name}")
        print(f"   • Dimensões: {src.width} x {src.height}")
        print(f"   • CRS: {src.crs}")
        
        # Calcular área do pixel
        transform = src.transform
        pixel_area_m2 = abs(transform.a * transform.e)
        
        # Ler dados da ortofoto
        if src.count >= 3:
            image_data = src.read([1, 2, 3])
            image_data = np.transpose(image_data, (1, 2, 0))  # HWC
        else:
            raise ValueError("A ortofoto deve ter pelo menos 3 canais (RGB)")
        
        # Normalizar se necessário
        if image_data.dtype != np.uint8:
            image_data = ((image_data - image_data.min()) / (image_data.max() - image_data.min()) * 255).astype(np.uint8)
        
        # Aplicar segmentação
        print("🔍 Aplicando segmentação...")
        segmentation_mask = segment_region_with_sliding_window(model, image_data, tile_size, overlap)
        
        # Salvar máscara georreferenciada
        output_geotiff = output_dir / "segmentacao_global.tif"
        with rasterio.open(
            output_geotiff,
            'w',
            driver='GTiff',
            height=src.height,
            width=src.width,
            count=1,
            dtype=segmentation_mask.dtype,
            crs=src.crs,
            transform=src.transform,
            compress='lzw'
        ) as dst:
            dst.write(segmentation_mask, 1)
        
        # Criar visualização colorida
        create_color_visualization(segmentation_mask, output_dir / "segmentacao_global_colorida.png")
        
        # Calcular estatísticas globais
        stats = calculate_area_statistics(segmentation_mask, pixel_area_m2)
        
        # Salvar resultados
        results = {
            'metadata': {
                'ortofoto': str(ortofoto_path),
                'processamento': datetime.now().isoformat(),
                'pixel_area_m2': pixel_area_m2,
                'crs': str(src.crs),
                'dimensoes': {'width': src.width, 'height': src.height}
            },
            'estatisticas_globais': stats
        }
        
        results_json = output_dir / "resultados_global.json"
        with open(results_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Processamento global concluído!")
        print(f"📁 Resultados salvos em: {output_dir}")
        print(f"   • Máscara: segmentacao_global.tif")
        print(f"   • Visualização: segmentacao_global_colorida.png")
        print(f"   • Estatísticas: resultados_global.json")
        
        # Mostrar estatísticas
        print(f"\n📊 ESTATÍSTICAS GLOBAIS:")
        for class_name, data in stats.items():
            print(f"   • {class_name}: {data['area_ha']:.2f} ha ({data['percentage']:.1f}%)")
        
        return results

def create_color_visualization(segmentation_mask, output_path):
    """
    Cria visualização colorida da máscara de segmentação.
    
    Args:
        segmentation_mask: Máscara de segmentação
        output_path: Caminho para salvar a imagem
    """
    height, width = segmentation_mask.shape
    color_mask = np.zeros((height, width, 3), dtype=np.uint8)
    
    for class_id, color in COLOR_MAP.items():
        mask_class = segmentation_mask == class_id
        color_mask[mask_class] = color
    
    # Salvar usando PIL
    color_image = Image.fromarray(color_mask, 'RGB')
    color_image.save(output_path)

def main():
    """Função principal com argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description='Segmentação de ortofotos com suporte a talhões')
    
    parser.add_argument('--mode', choices=['global', 'plots', 'auto'], default='auto',
                       help='Modo de processamento (padrão: auto)')
    parser.add_argument('--ortophoto', '-i', type=str,
                       help='Caminho para a ortofoto (TIF)')
    parser.add_argument('--shapefile', '-s', type=str,
                       help='Caminho para o shapefile dos talhões')
    parser.add_argument('--area-dir', '-d', type=str,
                       help='Diretório da área (auto-detecta arquivos)')
    parser.add_argument('--output-dir', '-o', type=str,
                       help='Diretório de saída')
    parser.add_argument('--checkpoint', type=str, default=DEFAULT_CHECKPOINT,
                       help='Checkpoint do modelo')
    parser.add_argument('--config', type=str, default=DEFAULT_CONFIG,
                       help='Configuração do modelo')
    parser.add_argument('--tile-size', type=int, default=256,
                       help='Tamanho dos tiles (padrão: 256)')
    parser.add_argument('--overlap', type=int, default=32,
                       help='Overlap entre tiles (padrão: 32)')
    parser.add_argument('--device', type=str, default='auto',
                       help='Dispositivo (auto, cuda, cpu)')
    
    args = parser.parse_args()
    
    # Configurar dispositivo
    if args.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    else:
        device = args.device
    
    print(f"🚀 SEGMENTAÇÃO DE ORTOFOTOS COM TALHÕES")
    print(f"🖥️  Dispositivo: {device}")
    print(f"📊 Modelo: {Path(args.checkpoint).name}")
    
    # Determinar arquivos de entrada
    if args.mode == 'auto' and args.area_dir:
        ortofoto_path, shapefile_path = find_files_in_area(args.area_dir)
        if ortofoto_path and shapefile_path:
            mode = 'plots'
        elif ortofoto_path:
            mode = 'global'
        else:
            print("❌ Nenhum arquivo válido encontrado na pasta")
            return
    else:
        ortofoto_path = args.ortophoto
        shapefile_path = args.shapefile
        mode = args.mode
    
    # Validar arquivos
    if not ortofoto_path or not os.path.exists(ortofoto_path):
        print("❌ Ortofoto não encontrada")
        return
    
    if mode == 'plots' and (not shapefile_path or not os.path.exists(shapefile_path)):
        print("❌ Shapefile não encontrado, mudando para modo global")
        mode = 'global'
    
    # Executar processamento
    try:
        if mode == 'plots':
            results = process_with_plots(
                ortofoto_path, shapefile_path, args.output_dir,
                args.checkpoint, args.config, args.tile_size, args.overlap, device
            )
        else:
            results = process_global(
                ortofoto_path, args.output_dir,
                args.checkpoint, args.config, args.tile_size, args.overlap, device
            )
        
        print(f"\n🎉 Processamento concluído com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
