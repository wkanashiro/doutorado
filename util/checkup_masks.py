import os
import cv2
import numpy as np
from tqdm import tqdm

mask_path = '/media/guatambu/hdd/wesley/daninhas_multiclasse_mmseg2/annotations/train'
unique_values = set()

print("Verificando valores únicos nas máscaras...")
for img_name in tqdm(os.listdir(mask_path)):
    img = cv2.imread(os.path.join(mask_path, img_name), cv2.IMREAD_UNCHANGED)
    unique_values.update(np.unique(img))

print(f"Valores encontrados nas suas máscaras: {sorted(list(unique_values))}")