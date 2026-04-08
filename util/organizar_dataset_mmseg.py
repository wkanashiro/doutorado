"""
Esse script organiza o dataset para o formato esperado pelo MMSegmentation.
Precisa ser passado para ele:
    - o dir base do dataset (que contém as pastas de cada classe, seguido das subpastas rgb e labels).
    - o dir destino onde os arquivos do dataset serão salvos no formato do MMSegmentation, ou seja, o pixel da máscara de anotação deve ser a classe correspondente 
        (0 para fundo, 1 para caruru, xx para branco)

* O script considera que o dataset já foi splitado em arquivos de texto (train.txt, val.txt, test.txt)

* O script considera que o dataset está organizado da seguinte forma:
base_dir/
    DATASET_CARURU/
        rgb/
            2025-09-12_604 - Santa Helena (Mardonio) - 02 - Survey - 12.12.2024 - Parte 03_C_rgb_32_92311_69162.jpg
            ...
        labels/
            2025-09-12_604 - Santa Helena (Mardonio) - 02 - Survey - 12.12.2024 - Parte 03_C_mask_32_92311_69162.png
            ...
    DATASET_GRAMINEA_PORTE_ALTO/
        rgb/
            2025-09-12_604 - Santa Helena (Mardonio) - 02 - Survey - 12.12.2024 - Parte 03_GA_rgb_32_92311_69162.jpg
            ...
        labels/
            2025-09-12_604 - Santa Helena (Mardonio) - 02 - Survey - 12.12.2024 - Parte 03_GA_mask_32_92311_69162.png
            ...
    ...


"""

import os
import numpy as np
import ast
import shutil
from pathlib import Path
from tqdm import tqdm
from PIL import Image

splits = {'train': 'train.txt', 'val': 'val.txt', 'test': 'test.txt'}

mapeamento_classes = {
    "DATASET_CARURU": 1,
    "DATASET_GRAMINEA_PORTE_ALTO": 2,
    "DATASET_GRAMINEA_PORTE_BAIXO": 3,
    "DATASET_MAMONA": 4,
    "DATASET_OUTRAS_FOLHAS_LARGAS": 5,
    "DATASET_TREPADEIRA": 6
}

def converter_mascara(path_origem, class_id):
    mask_color = Image.open(path_origem).convert('RGB')
    mask_color = np.array(mask_color)
    
    h, w, _ = mask_color.shape
    
    mask_gray = np.zeros((h, w), dtype=np.uint8) # Background = 0
    
    white_pixels = np.all(mask_color >= [255, 255, 255], axis=-1)
    mask_gray[white_pixels] = len(mapeamento_classes) + 1 # Área desconhecida. O "id" será o número de classes + 1
    
    foreground_pixels = np.all(mask_color == [255, 0, 0], axis=-1)
    mask_gray[foreground_pixels] = class_id # Classe correspondente
    
    # O que sobrar depois disso é o fundo validado, que já está como 0 (background)
    
    return Image.fromarray(mask_gray, mode='L')

"""
Formato esperado da linha do arquivo:
DATASET_OUTRAS_FOLHAS_LARGAS/('2025-09-12_604 - Santa Helena (Mardonio) - 02 - Survey - 12.12.2024 - Parte 03_C_mask_32_92311_69162', '.png')
"""
def parse_linha(linha):
    try:
        pasta_classe, tupla = linha.split('/', 1)
        nome_arquivo, _ = ast.literal_eval(tupla.strip())
        return pasta_classe, nome_arquivo
    except Exception as e:
        print(f"Erro ao processar a linha: {linha}. Detalhes do erro: {e}")
        return None, None
    
def organizar_dataset_mmseg(base_dir, output_dir):
    for split, arquivo_split in splits.items():
        base_dir = Path(base_dir)
        output_dir = Path(output_dir)
        
        (output_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output_dir / 'annotations' / split).mkdir(parents=True, exist_ok=True)
        
        with open(base_dir / arquivo_split, 'r') as f:
            linhas = f.readlines()
        
        for linha in tqdm(linhas, desc=f"Processando {split}"):
            pasta_classe, nome_arquivo = parse_linha(linha)
            
            if pasta_classe is None or nome_arquivo is None:
                continue
            
            class_id = mapeamento_classes.get(pasta_classe)
            if class_id is None:
                print(f"Aviso: Classe {pasta_classe} não encontrada no mapeamento. Pulando a linha: {linha}")
                continue
            
            novo_nome_arquivo = f"{class_id}_{nome_arquivo}"
            
            caminho_rgb = Path(base_dir) / pasta_classe / 'rgb' / f"{nome_arquivo}.jpg"
            caminho_labels = Path(base_dir) / pasta_classe / 'labels' / f"{nome_arquivo}.png"
            
            if caminho_rgb.exists() and caminho_labels.exists():
                # Copia a imagem RGB para o diretório de imagens do MMSegmentation
                shutil.copy(caminho_rgb, output_dir / 'images' / split / f"{novo_nome_arquivo}.jpg")
                
                # Converte a máscara de anotação e salva no diretório de anotações do MMSegmentation
                mascara_convertida = converter_mascara(caminho_labels, class_id)
                mascara_convertida.save(output_dir / 'annotations' / split / f"{novo_nome_arquivo}.png")
    
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organizar dataset para MMSegmentation")
    parser.add_argument("--base_dir", help="Diretório base do dataset")
    parser.add_argument("--output_dir", help="Diretório de saída")
    
    args = parser.parse_args()
    
    organizar_dataset_mmseg(args.base_dir, args.output_dir)