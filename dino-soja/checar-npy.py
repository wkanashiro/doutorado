import numpy as np
import os

# --- COLE O CAMINHO DA PASTA 'EXTRA' AQUI ---
# (A mesma que está no seu arquivo .yaml em 'extra=')
caminho_pasta_extra = "/media/guatambu/hdd/wesley/soja_patches_reduced_METADADOS/" 

arquivo_entries = os.path.join(caminho_pasta_extra, "entries-TRAIN.npy")
arquivo_classes = os.path.join(caminho_pasta_extra, "class-names-TRAIN.npy")

print(f"--- Inspecionando: {arquivo_entries} ---")

try:
    # Carrega os dados
    entries = np.load(arquivo_entries, mmap_mode='r')
    
    print(f"1. QUANTIDADE TOTAL DE IMAGENS: {len(entries)}")
    print(f"   (Esperado: ~1000. Se for ~6 milhões, o arquivo é velho)\n")

    print("2. AMOSTRA DAS PRIMEIRAS 5 ENTRADAS:")
    for i, entry in enumerate(entries[:5]):
        print(f"   Índice {i}: {entry}")

    print("\n3. VERIFICAÇÃO DE EXTENSÃO E NOME:")
    # Pega o primeiro caminho (entry costuma ser uma tupla ou string)
    exemplo = str(entries)
    print(f"   Primeiro arquivo listado: {exemplo}")
    
    if "soja_14.JPEG" in exemplo:
        print("   ALERTA VERMELHO: O metadado ainda contém os nomes antigos enumerados!")
    elif ".jpg" in exemplo or ".png" in exemplo:
        print("   ALERTA: A extensão no metadado não é .JPEG (maiúsculo)!")
    else:
        print("   Parece correto (nomes aleatórios e extensão .JPEG).")

except FileNotFoundError:
    print("ERRO: O arquivo entries-TRAIN.npy não foi encontrado neste caminho.")
    print("Verifique se você apontou para a pasta correta.")