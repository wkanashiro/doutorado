import os
import shutil
from pathlib import Path

def organizar_dataset_soja(list_path, target_path):
    """
    Organiza o dataset de soja no formato ImageNet esperado pelo DINOv3.
    - list_path contém um conjunto de caminhos para os patches de soja.
        list_path deve estar organizado da seguinte forma: 
            ["/caminho/para/classe1/rgb/", "/caminho/para/classe2/rgb/", ...]
    - target_path é o diretório onde o dataset organizado será salvo.
    O dataset será dividido em treino (80%) e validação (20%).
    
    A estrutura final será:
    target_path/
        train/
            soja/
                img1.jpg
                img2.jpg
                ...
        val/
            soja/
                imgA.jpg
                imgB.jpg
                ...
    """
    
    # Criar estrutura de diretórios
    train_dir = Path(target_path) / "train"
    val_dir = Path(target_path) / "val"
    
    # Criar diretório para classe única (self-supervised learning)
    train_class_dir = train_dir / "soja"
    val_class_dir = val_dir / "soja"
    
    train_class_dir.mkdir(parents=True, exist_ok=True)
    val_class_dir.mkdir(parents=True, exist_ok=True)
    
    
    
    # Listar todos os patches
    # list_path são varios caminhos para pastas rgb de diferentes classes de patches de soja
    
    total_patches = 0
    for path in list_path:
        path = Path(path)
        if not path.exists():
            print(f"Aviso: O caminho {path} não existe. Pulando...")
            continue
        
        patches = list(path.glob("*.jpg")) + list(path.glob("*.png"))
        if not patches:
            print(f"Aviso: Nenhum patch encontrado em {path}. Pulando...")
            continue
        
        print(f"Processando {path} com {len(patches)} patches")
        total_patches += len(patches)
        
        # Dividir em treino (80%) e validação (20%)
        split_idx = int(0.8 * len(patches))
        train_patches = patches[:split_idx]
        val_patches = patches[split_idx:]
        
        # Copiar arquivos
        print(f"Copiando patches de treino de {path}...")
        for patch in train_patches:
            shutil.copy2(patch, train_class_dir / patch.name)

    print(f"Encontrados {total_patches} patches")
    
    print(f"Dataset organizado:")
    print(f"  Treino: {len(train_patches)} patches")
    print(f"  Validação: {len(val_patches)} patches")
    print(f"  Localização: {target_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Organizar dataset de soja")
    parser.add_argument("--source_path", type=str, default="/media/lades/DISCO_01/soja_patches/224/rgb/", help="Caminho para os patches de soja")
    parser.add_argument("--target_path", type=str, default="/media/lades/DISCO_01/soja_patches/dataset_soja_dinov3", help="Caminho para o diretório de saída")
    args = parser.parse_args()

    organizar_dataset_soja(args.source_path, args.target_path)