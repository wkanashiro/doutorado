#!/usr/bin/env python3
"""
Script para inferência em ortofotos TIF usando sliding window
Pipeline MAE + MMSegmentation para segmentação semântica

Exemplos de uso:

1. Uso padrão (com caminhos padrão):
   python ortofoto_inference.py

2. Especificando arquivos:
   python ortofoto_inference.py --ortophoto /caminho/para/ortofoto.tif --output-geotiff /caminho/resultado.tif --output-png /caminho/visualizacao.png

3. Uso programático:
   from ortofoto_inference import process_ortophoto
   mask, color = process_ortophoto('/caminho/ortofoto.tif', '/caminho/resultado.tif')

4. Uso programático com main():
   from ortofoto_inference import main
   main('/caminho/ortofoto.tif', '/caminho/resultado.tif', '/caminho/visualizacao.png')
"""

import rasterio
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

def process_ortophoto_with_segmentation(
    ortophoto_path,
    checkpoint_path,
    config_path,
    output_geotiff_path,
    output_visualization_path,
    tile_size=256,
    overlap=32,
    batch_size=4,
    device='cuda' if torch.cuda.is_available() else 'cpu'
):
    """
    Processa uma ortofoto TIF usando sliding window para segmentação semântica.
    
    Args:
        ortophoto_path (str): Caminho para a ortofoto TIF de entrada
        checkpoint_path (str): Caminho para o checkpoint do modelo treinado
        config_path (str): Caminho para o arquivo de configuração do modelo
        output_geotiff_path (str): Caminho para salvar a máscara georreferenciada (GeoTIFF)
        output_visualization_path (str): Caminho para salvar a visualização colorida (PNG)
        tile_size (int): Tamanho dos tiles para sliding window
        overlap (int): Overlap entre tiles adjacentes
        batch_size (int): Tamanho do batch para inferência
        device (str): Dispositivo para inferência ('cuda' ou 'cpu')
    
    Returns:
        tuple: (segmentation_mask, color_mask)
    """
    
    print(f"Iniciando processamento da ortofoto: {ortophoto_path}")
    print(f"Tamanho do tile: {tile_size}x{tile_size}, Overlap: {overlap}")
    print(f"Dispositivo: {device}")
    
    # Carregar o modelo
    print("Carregando modelo...")
    model = init_model(config_path, checkpoint_path, device=device)
    
    # Abrir a ortofoto
    with rasterio.open(ortophoto_path) as src:
        height, width = src.height, src.width # Dimensões da ortofoto
        transform = src.transform # Transformação geoespacial
        crs = src.crs # Sistema de Referência de Coordenadas
        
        print(f"Dimensões da ortofoto: {width}x{height}")
        print(f"CRS: {crs}")
        
        # Ler dados da ortofoto (assumindo RGB)
        if src.count >= 3:
            image_data = src.read([1, 2, 3])  # R, G, B
            image_data = np.transpose(image_data, (1, 2, 0))  # HWC – altura, largura, canais: Isso é necessário para o inference_model do MMSegmentation
        else:
            raise ValueError(f"A ortofoto deve ter pelo menos 3 canais (RGB)")
        
        # Normalizar para 0-255 se necessário
        if image_data.dtype != np.uint8:
            image_data = ((image_data - image_data.min()) / (image_data.max() - image_data.min()) * 255).astype(np.uint8)
        
        # Inicializar a máscara de segmentação
        segmentation_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Calcular as posições dos tiles : Em outras palavras, onde cada recorte irá começar
        step = tile_size - overlap # Isso vai garantir a sobreposição dos patches
        x_positions = list(range(0, width - tile_size + 1, step))
        y_positions = list(range(0, height - tile_size + 1, step))
        
        # Adicionar tiles nas bordas se necessário
        if x_positions[-1] + tile_size < width:
            x_positions.append(width - tile_size)
        if y_positions[-1] + tile_size < height:
            y_positions.append(height - tile_size)
        
        total_tiles = len(x_positions) * len(y_positions)
        print(f"Total de tiles a processar: {total_tiles}")
        
        # Melhorar. Pode dar probelma de memória se a imagem for muito grande.
        # Verificar se o modelo está no modo de avaliação
        
        # Processar tiles
        with tqdm(total=total_tiles, desc="Processando tiles") as pbar:
            for y in y_positions:
                for x in x_positions:
                    # Extrair tile
                    y_end = min(y + tile_size, height)
                    x_end = min(x + tile_size, width)
                    
                    tile = image_data[y:y_end, x:x_end]
                    
                    # Pad se necessário
                    if tile.shape[0] < tile_size or tile.shape[1] < tile_size:
                        padded_tile = np.zeros((tile_size, tile_size, 3), dtype=np.uint8)
                        padded_tile[:tile.shape[0], :tile.shape[1]] = tile
                        tile = padded_tile
                    
                    # Fazer inferência
                    result = inference_model(model, tile)
                    pred_mask = result.pred_sem_seg.data.cpu().numpy()
                    
                    # Calcular região efetiva (sem padding)
                    eff_h = y_end - y
                    eff_w = x_end - x
                    
                    # Atualizar máscara de segmentação
                    
                    pred_resized = pred_mask[:eff_h, :eff_w]
                    segmentation_mask[y:y_end, x:x_end] = pred_resized
                    
                    pbar.update(1)
        
        # Salvar máscara georreferenciada
        print(f"Salvando máscara georreferenciada: {output_geotiff_path}")
        with rasterio.open(
            output_geotiff_path,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=segmentation_mask.dtype,
            crs=crs,
            transform=transform,
            compress='lzw'
        ) as dst:
            dst.write(segmentation_mask, 1)
        
        # Criar visualização colorida
        print(f"Criando visualização colorida: {output_visualization_path}")
        
        # Mapa de cores para as classes (conforme definido no daninhas.py)
        color_map = {
            0: [120, 120, 120], # Background - cinza
            1: [255, 0, 0],     # Gramínea Porte Alto - vermelho
            2: [0, 255, 0],     # Gramínea Porte Baixo - verde
            3: [0, 0, 255],     # Outras Folhas Largas - azul
            4: [0, 255, 255],   # Trepadeira - ciano
        }
        
        # Criar imagem colorida
        color_mask = np.zeros((height, width, 3), dtype=np.uint8)
        for class_id, color in color_map.items():
            mask_class = segmentation_mask == class_id
            color_mask[mask_class] = color
        
        # Salvar visualização
        try:
            # Usar PIL para salvar o PNG (mais confiável que cv2 para RGB)
            color_image = Image.fromarray(color_mask, 'RGB')
            color_image.save(output_visualization_path)
            print(f"✅ Visualização PNG salva: {output_visualization_path}")
        except Exception as e:
            print(f"❌ Erro ao salvar PNG: {e}")
            # Fallback: tentar com cv2
            try:
                success = cv2.imwrite(output_visualization_path, cv2.cvtColor(color_mask, cv2.COLOR_RGB2BGR))
                if success:
                    print(f"✅ Visualização PNG salva com cv2: {output_visualization_path}")
                else:
                    print(f"❌ cv2.imwrite falhou para: {output_visualization_path}")
            except Exception as e2:
                print(f"❌ Erro também no cv2: {e2}")
        
        # Calcular estatísticas
        print("\n=== ESTATÍSTICAS DE SEGMENTAÇÃO ===")
        
        # Nomes das classes conforme daninhas.py
        class_names = {
            0: 'Background',
            1: 'Gramínea Porte Alto', 
            2: 'Gramínea Porte Baixo',
            3: 'Outras Folhas Largas',
            4: 'Trepadeira'
        }
        
        unique_classes, counts = np.unique(segmentation_mask, return_counts=True)
        total_pixels = height * width
        
        for class_id, count in zip(unique_classes, counts):
            percentage = (count / total_pixels) * 100
            class_name = class_names.get(class_id, f'Classe {class_id}')
            print(f"{class_name} (ID: {class_id}): {count:,} pixels ({percentage:.2f}%)")
        
        print(f"\nProcessamento concluído!")
        
        return segmentation_mask, color_mask


def visualize_results(output_visualization_path, output_geotiff_path):
    """
    Visualiza os resultados da segmentação.
    
    Args:
        output_visualization_path (str): Caminho para a visualização PNG
        output_geotiff_path (str): Caminho para o GeoTIFF
    """
    print(f"🔍 Verificando arquivos de resultado...")
    print(f"   PNG: {output_visualization_path}")
    print(f"   TIF: {output_geotiff_path}")
    
    if os.path.exists(output_visualization_path):
        print("📊 Visualizando resultado da segmentação...")
        
        try:
            # Carregar e exibir a visualização colorida
            visualization = Image.open(output_visualization_path)
            
            plt.figure(figsize=(15, 10))
            plt.imshow(visualization)
            plt.title('Resultado da Segmentação Semântica - Ortofoto', fontsize=16)
            plt.axis('off')
            
            # Adicionar legenda das classes (cores conforme daninhas.py)
            legend_elements = [
                plt.Rectangle((0,0),1,1, facecolor=(120/255, 120/255, 120/255), label='Background'),
                plt.Rectangle((0,0),1,1, facecolor='red', label='Gramínea Porte Alto'),
                plt.Rectangle((0,0),1,1, facecolor='green', label='Gramínea Porte Baixo'), 
                plt.Rectangle((0,0),1,1, facecolor='blue', label='Outras Folhas Largas'),
                plt.Rectangle((0,0),1,1, facecolor='cyan', label='Trepadeira')
            ]
            plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
            
            plt.tight_layout()
            plt.show()
            
            print(f"✅ Visualização carregada com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao carregar visualização: {e}")
            
    else:
        print("⚠️  Arquivo de visualização PNG não encontrado.")
        print("Isso pode ter acontecido por:")
        print("   1. Erro durante o salvamento do PNG")
        print("   2. Problemas de permissão no diretório")
        print("   3. Espaço insuficiente em disco")
        print("   4. Erro na conversão de cores")
        
    # Verificar se pelo menos o GeoTIFF foi gerado
    if os.path.exists(output_geotiff_path):
        print(f"✅ Máscara georreferenciada encontrada: {output_geotiff_path}")
        
        # Tentar recriar o PNG a partir do GeoTIFF
        try:
            print("🔄 Tentando recriar PNG a partir do GeoTIFF...")
            with rasterio.open(output_geotiff_path) as src:
                mask_data = src.read(1)
                
            # Mapa de cores
            color_map = {
                0: [120, 120, 120], # Background - cinza
                1: [255, 0, 0],     # Gramínea Porte Alto - vermelho
                2: [0, 255, 0],     # Gramínea Porte Baixo - verde
                3: [0, 0, 255],     # Outras Folhas Largas - azul
                4: [0, 255, 255],   # Trepadeira - ciano
            }
            
            # Criar imagem colorida
            height, width = mask_data.shape
            color_mask = np.zeros((height, width, 3), dtype=np.uint8)
            for class_id, color in color_map.items():
                mask_class = mask_data == class_id
                color_mask[mask_class] = color
            
            # Salvar PNG
            color_image = Image.fromarray(color_mask, 'RGB')
            color_image.save(output_visualization_path)
            print(f"✅ PNG recriado com sucesso: {output_visualization_path}")
            
            # Tentar visualizar novamente
            visualize_results(output_visualization_path, output_geotiff_path)
            return
            
        except Exception as e:
            print(f"❌ Erro ao recriar PNG: {e}")
    else:
        print("❌ Nem o GeoTIFF foi encontrado!")
        
    print(f"📁 Arquivos esperados:")
    print(f"   - Máscara georreferenciada: {output_geotiff_path}")
    print(f"   - Visualização colorida: {output_visualization_path}")


def main(ortophoto_path=None, output_geotiff_path=None, output_visualization_path=None):
    """
    Função principal para executar o processamento de uma ortofoto.
    
    Args:
        ortophoto_path (str, optional): Caminho para a ortofoto de entrada
        output_geotiff_path (str, optional): Caminho para salvar o GeoTIFF de resultado
        output_visualization_path (str, optional): Caminho para salvar a visualização PNG
    """
    
    # Configurações do modelo treinado (fixas)
    checkpoint_path = '/home/lades/computer_vision/wesley/mae-soja/output_mae_soja-prof-wesley-17062025_200-epochs_mmsegmentation_5classes-40000iterations/iter_40000.pth'
    config_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation/configs/mae/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
    
    # Usar valores padrão se não fornecidos
    if ortophoto_path is None:
        ortophoto_path = "/home/lades/computer_vision/wesley/mae-soja/ortofotos/Ivinhema - 230 - Santista/230 - Santista 01 - 22 10 24 MGeo.tif"
    
    if output_geotiff_path is None:
        output_dir = '/home/lades/computer_vision/wesley/mae-soja'
        output_geotiff_path = os.path.join(output_dir, 'resultado_segmentacao_ortofoto.tif')
    
    if output_visualization_path is None:
        # Gerar automaticamente baseado no geotiff_path
        base_path = os.path.splitext(output_geotiff_path)[0]
        output_visualization_path = f"{base_path}_visualizacao.png"
    
    # Verificar se a ortofoto existe
    if not os.path.exists(ortophoto_path):
        print(f"⚠️  ATENÇÃO: Ortofoto não encontrada em: {ortophoto_path}")
        print("Por favor, ajuste o caminho da ortofoto.")
        print("\nExemplo de caminhos possíveis:")
        print("- /home/lades/computer_vision/wesley/mae-soja/ortofoto_soja.tif")
        print("- /home/lades/computer_vision/wesley/sua_ortofoto.tif")
        return
    
    # Verificar se os arquivos do modelo existem
    if not os.path.exists(checkpoint_path):
        print(f"❌ ERRO: Checkpoint do modelo não encontrado: {checkpoint_path}")
        return
        
    if not os.path.exists(config_path):
        print(f"❌ ERRO: Arquivo de configuração não encontrado: {config_path}")
        return
    
    # Criar diretórios de saída se não existirem
    for output_path in [output_geotiff_path, output_visualization_path]:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            print(f"📁 Diretório criado: {output_dir}")
    
    print("Iniciando processamento da ortofoto...")
    print(f"📍 Ortofoto: {ortophoto_path}")
    print(f"📊 Modelo: {checkpoint_path}")
    print(f"⚙️  Configuração: {config_path}")
    print(f"💾 GeoTIFF resultado: {output_geotiff_path}")
    print(f"🖼️  PNG visualização: {output_visualization_path}")
    
    try:
        # Executar processamento
        segmentation_mask, color_mask = process_ortophoto_with_segmentation(
            ortophoto_path=ortophoto_path,
            checkpoint_path=checkpoint_path,
            config_path=config_path,
            output_geotiff_path=output_geotiff_path,
            output_visualization_path=output_visualization_path,
            tile_size=256,
            overlap=32,
            batch_size=4
        )
        
        print("\n✅ Processamento concluído com sucesso!")
        
        # Visualizar resultados
        visualize_results(output_visualization_path, output_geotiff_path)
        
    except Exception as e:
        print(f"\n❌ Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()


def process_ortophoto(ortophoto_path, output_geotiff_path=None, output_visualization_path=None, 
                     tile_size=256, overlap=32, batch_size=4):
    """
    Função de conveniência para processar uma ortofoto com parâmetros personalizados.
    
    Args:
        ortophoto_path (str): Caminho para a ortofoto de entrada
        output_geotiff_path (str, optional): Caminho para salvar o GeoTIFF de resultado
        output_visualization_path (str, optional): Caminho para salvar a visualização PNG
        tile_size (int): Tamanho dos tiles para sliding window
        overlap (int): Overlap entre tiles adjacentes
        batch_size (int): Tamanho do batch para inferência
        
    Returns:
        tuple: (segmentation_mask, color_mask)
    """
    return main(ortophoto_path, output_geotiff_path, output_visualization_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Processamento de ortofoto com segmentação semântica')
    parser.add_argument('--ortophoto', '-i', type=str, 
                       help='Caminho para a ortofoto de entrada (formato TIF)')
    parser.add_argument('--output-geotiff', '-o', type=str,
                       help='Caminho para salvar o GeoTIFF de resultado')
    parser.add_argument('--output-png', '-p', type=str,
                       help='Caminho para salvar a visualização PNG')
    parser.add_argument('--tile-size', type=int, default=256,
                       help='Tamanho dos tiles para sliding window (padrão: 256)')
    parser.add_argument('--overlap', type=int, default=32,
                       help='Overlap entre tiles adjacentes (padrão: 32)')
    parser.add_argument('--batch-size', type=int, default=4,
                       help='Tamanho do batch para inferência (padrão: 4)')
    
    args = parser.parse_args()
    
    # Se argumentos foram fornecidos, usar eles; senão usar valores padrão
    if len(sys.argv) > 1:
        main(ortophoto_path=args.ortophoto, 
             output_geotiff_path=args.output_geotiff, 
             output_visualization_path=args.output_png)
    else:
        # Executar com valores padrão se nenhum argumento foi fornecido
        main()
