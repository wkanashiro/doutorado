#!/usr/bin/env python3
"""
Teste simplificado do processamento por talhões - processa apenas 1 talhão para validar o pipeline
"""

import rasterio
from rasterio.mask import mask
import numpy as np
from mmseg.apis import init_model, inference_model
import geopandas as gpd
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def test_single_plot_processing():
    """Testa processamento de um único talhão."""
    
    print("🧪 TESTE: PROCESSAMENTO DE TALHÃO ÚNICO")
    print("="*50)
    
    # Configurações
    ortofoto_path = "/home/lades/computer_vision/wesley/mae-soja/ortofotos_soja/Angelica - 198 - Figueira (Scatolin) - Gleba 04/198 - Figueira (Scatolin) 04 Soja - 08 01 25 Survey-002.tif"
    shapefile_path = "/home/lades/computer_vision/wesley/mae-soja/ortofotos_soja/Angelica - 198 - Figueira (Scatolin) - Gleba 04/198_Figueira_Scatolin_04_08_01_25_Talhoes.shp"
    checkpoint_path = '/home/lades/computer_vision/wesley/mae-soja/output_mae_soja-prof-wesley-17062025_200-epochs_mmsegmentation_5classes-40000iterations/iter_40000.pth'
    config_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation/configs/mae/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
    output_dir = Path("/home/lades/computer_vision/wesley/mae-soja/teste_talhao_unico")
    
    output_dir.mkdir(exist_ok=True)
    
    # Carregar modelo
    print("🤖 Carregando modelo...")
    model = init_model(config_path, checkpoint_path, device='cuda')
    
    # Carregar shapefile
    print("📂 Carregando shapefile...")
    gdf = gpd.read_file(shapefile_path)
    print(f"   • {len(gdf)} talhões encontrados")
    
    # Pegar o primeiro talhão (maior) para teste
    first_plot = gdf.iloc[0]
    plot_geom = [first_plot.geometry.__geo_interface__]
    
    print(f"📍 Processando talhão 0 (área: {first_plot.get('area_ha', 'N/A')} ha)")
    
    # Abrir ortofoto e extrair região do talhão
    with rasterio.open(ortofoto_path) as src:
        print(f"   • Ortofoto: {src.width} x {src.height}")
        print(f"   • CRS: {src.crs}")
        
        # Mascarar para este talhão
        masked_data, masked_transform = mask(src, plot_geom, crop=True)
        
        if masked_data.size == 0:
            print("❌ Região vazia após crop")
            return
        
        print(f"   • Região extraída: {masked_data.shape}")
        
        # Converter para HWC
        if len(masked_data.shape) == 3 and masked_data.shape[0] >= 3:
            masked_image = np.transpose(masked_data[:3], (1, 2, 0))
        else:
            print("❌ Formato de dados inesperado")
            return
        
        print(f"   • Imagem processada: {masked_image.shape}")
        
        # Normalizar se necessário
        if masked_image.dtype != np.uint8:
            valid_mask = masked_image.sum(axis=2) > 0
            if valid_mask.any():
                masked_image = ((masked_image - masked_image.min()) / (masked_image.max() - masked_image.min()) * 255).astype(np.uint8)
        
        # Aplicar segmentação (tile único se região for pequena)
        print("🔍 Aplicando segmentação...")
        height, width = masked_image.shape[:2]
        
        if height > 256 or width > 256:
            # Redimensionar para caber em um tile
            scale_factor = min(256/height, 256/width, 1.0)
            new_height = int(height * scale_factor)
            new_width = int(width * scale_factor)
            
            import cv2
            resized_image = cv2.resize(masked_image, (new_width, new_height))
            print(f"   • Redimensionado para: {resized_image.shape}")
            
            # Pad para 256x256
            padded_image = np.zeros((256, 256, 3), dtype=np.uint8)
            padded_image[:new_height, :new_width] = resized_image
            
            # Segmentação
            result = inference_model(model, padded_image)
            pred_mask = result.pred_sem_seg.data.cpu().numpy()
            
            # Extrair região válida
            pred_mask = pred_mask[:new_height, :new_width]
            
            # Redimensionar de volta
            final_mask = cv2.resize(pred_mask.astype(np.uint8), (width, height), interpolation=cv2.INTER_NEAREST)
        else:
            # Pad se necessário
            padded_image = np.zeros((256, 256, 3), dtype=np.uint8)
            padded_image[:height, :width] = masked_image
            
            # Segmentação
            result = inference_model(model, padded_image)
            pred_mask = result.pred_sem_seg.data.cpu().numpy()
            
            final_mask = pred_mask[:height, :width]
        
        print(f"   • Máscara final: {final_mask.shape}")
        
        # Salvar resultado
        output_tif = output_dir / "talhao_000_segmentacao.tif"
        with rasterio.open(
            output_tif,
            'w',
            driver='GTiff',
            height=final_mask.shape[0],
            width=final_mask.shape[1],
            count=1,
            dtype=final_mask.dtype,
            crs=src.crs,
            transform=masked_transform,
            compress='lzw'
        ) as dst:
            dst.write(final_mask, 1)
        
        # Calcular estatísticas
        pixel_area_m2 = abs(masked_transform.a * masked_transform.e)
        unique_classes, counts = np.unique(final_mask, return_counts=True)
        total_pixels = final_mask.size
        
        stats = {}
        class_names = {
            0: 'Background',
            1: 'Gramínea Porte Alto',
            2: 'Gramínea Porte Baixo', 
            3: 'Outras Folhas Largas',
            4: 'Trepadeira'
        }
        
        for class_id, count in zip(unique_classes, counts):
            area_m2 = count * pixel_area_m2
            area_ha = area_m2 / 10000
            percentage = (count / total_pixels) * 100
            
            class_name = class_names.get(class_id, f'Classe {class_id}')
            stats[class_name] = {
                'class_id': int(class_id),
                'pixels': int(count),
                'area_m2': float(area_m2),
                'area_ha': float(area_ha),
                'percentage': float(percentage)
            }
        
        # Salvar estatísticas
        result_data = {
            'talhao_id': 0,
            'area_total_ha': float(first_plot.get('area_ha', 0)),
            'estatisticas': stats,
            'metadata': {
                'processamento': datetime.now().isoformat(),
                'pixel_area_m2': pixel_area_m2,
                'dimensoes': {'height': height, 'width': width}
            }
        }
        
        results_json = output_dir / "estatisticas_talhao_000.json"
        with open(results_json, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Teste concluído!")
        print(f"📁 Resultados salvos em: {output_dir}")
        print(f"   • Máscara: {output_tif}")
        print(f"   • Estatísticas: {results_json}")
        
        print(f"\n📊 ESTATÍSTICAS DO TALHÃO:")
        for class_name, data in stats.items():
            print(f"   • {class_name}: {data['area_ha']:.2f} ha ({data['percentage']:.1f}%)")
        
        return result_data

if __name__ == "__main__":
    test_single_plot_processing()
