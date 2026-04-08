import os
import cv2
import numpy as np
import random
from tqdm import tqdm

def gerar_splits_estratificados(base_dir, output_dir, prop_train=0.8, prop_val=0.1):
    classes = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    print(f"Classes encontradas: {classes}\n")
    
    train_list = []
    val_list = []
    test_list = []

    # Semente fixa para garantir que o split seja sempre o mesmo se você rodar novamente
    random.seed(42)

    for pasta_classe in classes:
        caminho_labels = os.path.join(base_dir, pasta_classe, "labels")
        
        if not os.path.exists(caminho_labels):
            print(f"Aviso: Pasta {caminho_labels} não encontrada.")
            continue
            
        imagens_classe = [f for f in os.listdir(caminho_labels) if f.endswith(('.png', '.jpg'))]
        
        imagens_com_daninha = []
        imagens_so_fundo = []
        
        print(f"Analisando máscaras da classe: {pasta_classe}...")
        for img_nome in tqdm(imagens_classe):
            caminho_img = os.path.join(caminho_labels, img_nome)
            
            # Carrega a máscara de anotação
            img_rgb = cv2.imread(caminho_img)
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
            
            # Condição: Identificando as cores da máscara
            # Pixels brancos (área não analisada pelo especialista)
            mask_branca = np.all(img_rgb >= 250, axis=-1)
            # Pixels pretos (área de fundo validada)
            mask_preta = np.all(img_rgb <= 5, axis=-1)
            
            # O que não for nem branco e nem preto é a daninha colorida
            mask_daninha = ~(mask_branca | mask_preta)
            
            # O MMSegmentation prefere caminhos relativos sem a extensão do arquivo
            nome_base = os.path.splitext(img_nome)
            caminho_relativo = f"{pasta_classe}/{nome_base}"
            
            if np.any(mask_daninha):
                imagens_com_daninha.append(caminho_relativo)
            else:
                imagens_so_fundo.append(caminho_relativo)
                
        # =========================================================
        # O SPLIT ESTRATIFICADO (80/10/10) NAS IMAGENS COM MATO
        # =========================================================
        random.shuffle(imagens_com_daninha)
        total_validas = len(imagens_com_daninha)
        
        qtd_train = int(total_validas * prop_train)
        qtd_val = int(total_validas * prop_val)
        # O restante fica para o conjunto de teste
        
        treino_classe = imagens_com_daninha[:qtd_train]
        val_classe = imagens_com_daninha[qtd_train:qtd_train+qtd_val]
        teste_classe = imagens_com_daninha[qtd_train+qtd_val:]
        
        # As imagens sem daninha vão estritamente para o treino
        train_list.extend(treino_classe + imagens_so_fundo)
        val_list.extend(val_classe)
        test_list.extend(teste_classe)
        
        print(f"  -> Com daninha: {total_validas} | Só fundo: {len(imagens_so_fundo)}")
        print(f"  -> Separação: Treino={len(treino_classe)+len(imagens_so_fundo)} (incluindo as de fundo), Val={len(val_classe)}, Test={len(teste_classe)}\n")

    # =========================================================
    # GERAÇÃO DOS ARQUIVOS .TXT PARA O MMSEGMENTATION
    # =========================================================
    os.makedirs(output_dir, exist_ok=True)
    
    for nome_arquivo, lista in zip(["train.txt", "val.txt", "test.txt"], [train_list, val_list, test_list]):
        caminho_txt = os.path.join(output_dir, nome_arquivo)
        with open(caminho_txt, "w") as f:
            for item in lista:
                f.write(f"{item}\n")
                
    print("="*60)
    print("Divisão estratificada concluída!")
    print(f"Total em Treino : {len(train_list):,} imagens")
    print(f"Total em Valid  : {len(val_list):,} imagens")
    print(f"Total em Teste  : {len(test_list):,} imagens")
    print(f"Arquivos txt salvos em: {output_dir}")
    print("="*60)
    
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerar splits estratificados para o MMSegmentation")
    parser.add_argument("--base_dir", type=str, required=True, help="Diretório base do dataset (ex: /home/usuario/dataset)")
    parser.add_argument("--output_dir", type=str, required=True, help="Diretório onde os arquivos .txt serão salvos (ex: /home/usuario/splits)")
    parser.add_argument("--prop_train", type=float, default=0.8, help="Proporção de imagens com daninha para o conjunto de treino (default: 0.8)")
    parser.add_argument("--prop_val", type=float, default=0.1, help="Proporção de imagens com daninha para o conjunto de validação (default: 0.1)")
    args = parser.parse_args()
    
    gerar_splits_estratificados(args.base_dir, args.output_dir, args.prop_train, args.prop_val)