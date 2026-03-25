import sys
import os

# Garante que o python encontre o módulo dinov3
sys.path.append(os.getcwd())

from dinov3.data.datasets import ImageNet

# Caminhos definidos no passo anterior
ROOT_DIR = "/media/guatambu/hdd/wesley/soja_patches_6M/"
EXTRA_DIR = "/media/guatambu/hdd/wesley/soja_patches_6M_extra/"

if not os.path.exists(EXTRA_DIR):
    os.makedirs(EXTRA_DIR)

print("Gerando metadados..")

# Gera para Treino
print("Processando TRAIN...")
dataset_train = ImageNet(split=ImageNet.Split.TRAIN, root=ROOT_DIR, extra=EXTRA_DIR)
dataset_train.dump_extra()

# Gera para Validação
print("Processando VAL...")
dataset_val = ImageNet(split=ImageNet.Split.VAL, root=ROOT_DIR, extra=EXTRA_DIR)
dataset_val.dump_extra()

print("Concluído! Arquivos .npy gerados em", EXTRA_DIR)