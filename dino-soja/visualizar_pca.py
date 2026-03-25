import torch
import torch.nn as nn
from torchvision import transforms as pth_transforms
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# --- CONFIGURAÇÕES ---
# Caminho do repo (para carregar a arquitetura)
REPO_DIR = "/home/guatambu/Documentos/kanashiro/doutorado/dino-soja/dinov3"
# Caminho do seu checkpoint recém-treinado
CHECKPOINT_PATH = "/home/guatambu/Documentos/kanashiro/doutorado/dino-soja/dinov3/output_soja_run_6M/eval/training_124999/teacher_checkpoint.pth" 
# Uma imagem aleatoria do diretorio
DATASET_DIR = "/media/guatambu/hdd/wesley/daninhas_multiclasse/DATASET_TREPADEIRA/rgb/"

# Obtém o nome de uma imagem aleatória de DATASET_DIR
import os
import random
all_images = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
random_image_name = random.choice(all_images)
IMAGE_PATH = os.path.join(DATASET_DIR, random_image_name)

print(f"Usando a imagem: {IMAGE_PATH}")

# Arquitetura (use a mesma do treino: vits16 ou vitl16)
ARCH = "vitl16" 

# --- 1. CARREGAR O MODELO ---
import sys
sys.path.append(REPO_DIR)
# Importa dinamicamente a arquitetura correta
if ARCH == "vits16":
    from dinov3.models.vision_transformer import vit_small as build_model
elif ARCH == "vitl16":
    from dinov3.models.vision_transformer import vit_large as build_model

model = build_model()
# Carrega os pesos
checkpoint = torch.load(CHECKPOINT_PATH, map_location='cpu')
# Limpa o nome das chaves (remove 'teacher.' e 'backbone.')
state_dict = checkpoint['teacher']
state_dict = {k.replace("module.", "").replace("backbone.", ""): v for k, v in state_dict.items()}
msg = model.load_state_dict(state_dict, strict=False)
print(f"Pesos carregados: {msg}")

model.cuda()
model.eval()

# --- 2. PREPARAR A IMAGEM ---
W, H = 256, 256  # Tamanho original da imagem
transform = pth_transforms.Compose([
    pth_transforms.Resize((W, H)), # Tamanho bom para visualização
    pth_transforms.ToTensor(),
    pth_transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
])

img_pil = Image.open(IMAGE_PATH).convert('RGB')
img_tensor = transform(img_pil).unsqueeze(0).cuda()

# --- 3. EXTRAIR FEATURES E CALCULAR PCA ---
with torch.no_grad():
    features_dict = model.forward_features(img_tensor)
    features = features_dict["x_norm_patchtokens"] 
    # features shape original: [Batch=1, NumPatches=1024, Dim=384]
    
    features = features.cpu().numpy()

# --- CORREÇÃO DO ERRO ---
# Removemos a dimensão do batch (índice 0)
# Agora shape é  -> Aceito pelo PCA
features_flat = features[0]

print(f"Shape para o PCA: {features_flat.shape}")

# Calcula PCA para reduzir para 3 dimensões (RGB)
pca = PCA(n_components=3)
pca.fit(features_flat)
pca_features = pca.transform(features_flat)

# Normaliza para 0-1 para virar imagem RGB
pca_features = (pca_features - pca_features.min(0)) / (pca_features.max(0) - pca_features.min(0))

# Recupera o formato espacial (H/patch_size, W/patch_size)
# Se imagem é 512 e patch é 16 -> 32x32
spatial_size = W // 16
pca_img = pca_features.reshape(spatial_size, spatial_size, 3)

# --- 4. PLOTAR ---
plt.figure(figsize=(10, 5))

# Imagem Original
plt.subplot(1, 2, 1)
plt.imshow(img_pil.resize((512, 512)))
plt.title("Imagem Original")
plt.axis('off')

# PCA
plt.subplot(1, 2, 2)
plt.imshow(pca_img)
plt.title("DINOv3 PCA (Sem máscara)")
plt.axis('off')

plt.show()