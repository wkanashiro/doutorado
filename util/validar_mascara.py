import numpy as np
import sys
from PIL import Image
import os
import random

def verificar_mascara(path):
    print(f"\n🔍 Analisando máscara: {os.path.basename(path)}")
    
    if not os.path.exists(path):
        print(f"❌ Erro: Arquivo não encontrado em {path}")
        return

    try:
        # 1. Abre com PIL e garante o modo 'L' (Grayscale 8-bit)
        img_pil = Image.open(path)
        if img_pil.mode != 'L':
            print(f"⚠️ Aviso: A imagem estava em modo {img_pil.mode}, convertendo para 'L'.")
            img_pil = img_pil.convert('L')
        
        # 2. Converte para array NumPy para análise matemática
        img_np = np.array(img_pil)
        
        # 3. Encontra os valores únicos de pixel
        valores_unicos = np.unique(img_np)

        print(f"✅ Valores únicos encontrados: {valores_unicos}")
        
        print("\nAnálise:")
        if 0 in valores_unicos: print("   - Contém pixels de Fundo (0)")
        if 255 in valores_unicos: print("   - Contém pixels para Ignorar/Região Branca (255)")
        
        # Checa se há IDs de classe (entre 1 e 6)
        ids_classe = [v for v in valores_unicos if 0 < v < 255]
        if ids_classe:
            print(f"   - Contém pixels de ID de Classe: {ids_classe}")
        else:
            print("   ⚠️ AVISO: Não contém pixels de ID de classe (apenas fundo/ignore). Isso pode ocorrer em algumas fotos, mas verifique se não está acontecendo em todas.")

    except Exception as e:
        print(f"❌ Ocorreu um erro ao ler a imagem: {e}")

if __name__ == "__main__":
    dataset_dir = "/media/guatambu/hdd/wesley/daninhas_multiclasse_mmseg"

    annotations_dir = os.path.join(dataset_dir, "annotations", "train")
    anotacoes = [f for f in os.listdir(annotations_dir) if f.endswith('.png')]
    
    for i in range(10):  # Verificar 10 máscaras diferentes
        PATH_DA_MASCARA = os.path.join(annotations_dir, random.choice(anotacoes))
        verificar_mascara(PATH_DA_MASCARA)