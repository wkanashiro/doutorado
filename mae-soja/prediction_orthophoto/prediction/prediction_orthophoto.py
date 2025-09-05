from utils.tif import get_image_patch
from utils.shp2img import get_img
from utils.img2shp import polygons_from_binary_image

import geopandas as gpd
import pandas as pd
import rasterio
import numpy as np
from tqdm import tqdm
import torch.nn.functional as F
from mmseg.apis import inference_model

def prediction_in_plot(gpd_talhoes, index, dataset, model, patch_size, step, min_img_size=256, batch_size=32):
    mask, (min_x, min_y, max_x, max_y), (min_lat, max_lat, min_lon, max_lon) = get_img(gpd_talhoes, dataset.index, index=index, min_img_size=min_img_size)
    min_x, min_y, max_x, max_y = int(min_x), int(min_y), int(max_x), int(max_y)
    width, height = int(max_x-min_x), int(max_y-min_y)

    # Verifica se o talhão é muito grande para a memória disponível
    estimated_memory_gb = (5 * width * height * 8) / (1024**3)  # 5 classes, 8 bytes por float64
    print(f"📏 Talhão {index+1}: {width} x {height} pixels (~{estimated_memory_gb:.1f} GB)")
    
    if estimated_memory_gb > 16:  # Limite de 16GB
        print(f"⚠️ Talhão muito grande ({estimated_memory_gb:.1f} GB). Pulando...")
        raise MemoryError(f"Talhão requer {estimated_memory_gb:.1f} GB de memória")

    imgs = []
    positions = []    
    
    # Inicializar results_probs como None para detecção dinâmica de classes
    results_probs = None

    for x in tqdm(range(min_x, max_x-1, step)):
        discard_x1, discard_x2 = 0.1, 0.9
        if x == min_x:
            discard_x1 = 0.
        if x+patch_size >= max_x:
            x = max_x-patch_size
            discard_x2 = 1.
        for y in range(min_y, max_y-1, step):
            discard_y1, discard_y2 = 0.1, 0.9
            if y+patch_size >= max_y:
                discard_y2 = 1.
                y = max_y-patch_size
            if y == min_y:
                discard_y1 = 0.

            x1 = (x-min_x)+int(patch_size*discard_x1)
            y1 = (y-min_y)+int(patch_size*discard_y1)
            x2 = (x-min_x)+int(patch_size*discard_x2)
            y2 = (y-min_y)+int(patch_size*discard_y2)

            mask_patch = mask[x1:x2, y1:y2]
            if np.sum(mask_patch) == 0:
                continue

            img = get_image_patch(dataset, x, y, patch_size, patch_size)
            if img is None:
                continue

            img = img[:, :, [2, 1, 0]]
            imgs.append(img)
            positions.append([x1, x2, y1, y2, discard_x1, discard_x2, discard_y1, discard_y2, x, y])

            if len(imgs) >= batch_size:
                results_all = inference_model(model, imgs)

                for i in range(len(results_all)):
                    x1, x2, y1, y2, discard_x1, discard_x2, discard_y1, discard_y2, x, y = positions[i]
                    patch_daninha = F.softmax(results_all[i].seg_logits.data, dim=0).cpu().numpy()
                    patch_daninha = patch_daninha[:, int(patch_size*discard_x1):int(patch_size*discard_x2), int(patch_size*discard_y1):int(patch_size*discard_y2)]
                    
                    # Inicializa results_probs dinamicamente baseado no número de classes
                    if results_probs is None:
                        num_classes = patch_daninha.shape[0]
                        try:
                            results_probs = np.zeros((num_classes, width, height), dtype=np.float32)
                            print(f"📊 Detectadas {num_classes} classes no modelo")
                        except (MemoryError, np.core._exceptions._ArrayMemoryError) as e:
                            print(f"❌ Erro de memória ao alocar array para {num_classes} classes: {e}")
                            raise MemoryError(f"Não foi possível alocar memória para {num_classes} classes")
                    
                    results_probs[:, x1:x2, y1:y2] = results_probs[:, x1:x2, y1:y2] + patch_daninha
                imgs = []
                positions = []

    if len(imgs) > 0:
        results_all = inference_model(model, imgs)

        for i in range(len(results_all)):
            x1, x2, y1, y2, discard_x1, discard_x2, discard_y1, discard_y2, x, y = positions[i]
            patch_daninha = F.softmax(results_all[i].seg_logits.data, dim=0).cpu().numpy()
            patch_daninha = patch_daninha[:, int(patch_size*discard_x1):int(patch_size*discard_x2), int(patch_size*discard_y1):int(patch_size*discard_y2)]
            
            # Inicializa results_probs dinamicamente se ainda não foi criado
            if results_probs is None:
                num_classes = patch_daninha.shape[0]
                try:
                    results_probs = np.zeros((num_classes, width, height), dtype=np.float32)
                    print(f"📊 Detectadas {num_classes} classes no modelo")
                except (MemoryError, np.core._exceptions._ArrayMemoryError) as e:
                    print(f"❌ Erro de memória ao alocar array para {num_classes} classes: {e}")
                    raise MemoryError(f"Não foi possível alocar memória para {num_classes} classes")
                                    
            results_probs[:, x1:x2, y1:y2] = results_probs[:, x1:x2, y1:y2] + patch_daninha

    results = np.argmax(results_probs, axis=0).astype(np.uint8)   
    if mask is not None:
        results[mask == 0] = 0

    results_shp = polygons_from_binary_image(results, dataset.transform, dataset.crs, min_x=min_x, min_y=min_y)
    return results, results_shp
    
def prediction(shp_path, tif_path, model, patch_size, step):
    gpd_talhoes = gpd.read_file(shp_path)
    dataset = rasterio.open(tif_path)
    gpd_talhoes = gpd_talhoes.to_crs(dataset.crs)
    shp_all_talhoes = []
    talhoes_processados = 0
    talhoes_pulados = 0

    for i, index in enumerate(range(len(gpd_talhoes))):
        print(f'\tProcessando talhão: {i+1}/{len(gpd_talhoes)}')
        try:
            _, results_shp = prediction_in_plot(gpd_talhoes, index, dataset, model, patch_size, step)
            shp_all_talhoes.append(results_shp)
            talhoes_processados += 1
        except MemoryError as e:
            print(f"🚫 Talhão {i+1} pulado por falta de memória: {e}")
            talhoes_pulados += 1
            continue
        except Exception as e:
            print(f"❌ Erro inesperado no talhão {i+1}: {e}")
            talhoes_pulados += 1
            continue

    print(f"\n📊 Resumo do processamento:")
    print(f"   ✅ Talhões processados: {talhoes_processados}")
    print(f"   🚫 Talhões pulados: {talhoes_pulados}")
    print(f"   📝 Total: {len(gpd_talhoes)}")

    if len(shp_all_talhoes) == 0:
        print("⚠️ Nenhum talhão foi processado com sucesso!")
        return gpd.GeoDataFrame(columns=['geometry'], crs=dataset.crs)

    # Concatenando uma lista de GeoDataFrames
    gdf_all_talhoes = gpd.GeoDataFrame(pd.concat(shp_all_talhoes, ignore_index=True), crs=dataset.crs)
    return gdf_all_talhoes
