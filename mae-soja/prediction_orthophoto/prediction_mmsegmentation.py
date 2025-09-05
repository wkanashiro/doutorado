import sys
import os

# Agora usando mmsegmentation LOCAL com mmcv 2.0.0 compatível
# ========================================================================
mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
if mmseg_local_path not in sys.path:
    sys.path.insert(0, mmseg_local_path)
    print(f"✓ Usando mmsegmentation LOCAL: {mmseg_local_path}")

from models.load import get_mmsegmentation_model
from utils.files import find_subfolders_in_folder, find_tif_shp_in_folder
from prediction.prediction_orthophoto import prediction

import os

config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
device = 'cuda:0'

patch_size = 256
step = patch_size // 2

path_folder = '/home/lades/computer_vision/wesley/mae-soja/data/input/ortofotos_soja/'

model = get_mmsegmentation_model(config_file, checkpoint_file, device)

orto_paths = find_subfolders_in_folder(path_folder, extensions=['.tif', '.shp'])  

print("---------------------------- Iniciando processamento ---------------------------- ")
print(f"Total de ortofotos as serem processados: {len(orto_paths)}\n")

ortofotos_processadas = 0
ortofotos_com_erro = 0

for o, orto_path in enumerate(orto_paths):
    print(f'Processando ortofoto: {(o+1)}/{len(orto_paths)}: {orto_path}')
    # Caminho da ortofoto
    filename_orto = os.path.basename(orto_path)[:-4]
    tif_path, shp_path = find_tif_shp_in_folder(orto_path)
    
    if tif_path is None:
        print(f'Nenhum arquivo .tif encontrado em {tif_path}')
        continue

    if shp_path is None:
        print(f'Nenhum arquivo .shp encontrado em {shp_path}')
        continue

    try:
        shp = prediction(shp_path, tif_path, model, patch_size, step)
        
        if len(shp) > 0:
            output_file = os.path.join(orto_path, f'./prediction_{filename_orto}.shp')
            shp.to_file(output_file)
            print(f"✅ Ortofoto processada com sucesso: {filename_orto}")
            print(f"📊 Resultados salvos: {len(shp)} polígonos em {output_file}")
            ortofotos_processadas += 1
        else:
            print(f"⚠️ Nenhum resultado gerado para: {filename_orto} (todos os talhões foram pulados)")
    
    except Exception as e:
        print(f"❌ Erro ao processar ortofoto {filename_orto}: {e}")
        ortofotos_com_erro += 1
        continue

print("\n" + "=" * 70)
print("RESUMO FINAL DO PROCESSAMENTO")
print("=" * 70)
print(f"📂 Total de ortofotos: {len(orto_paths)}")
print(f"✅ Ortofotos processadas: {ortofotos_processadas}")
print(f"❌ Ortofotos com erro: {ortofotos_com_erro}")
print(f"⏭️ Ortofotos puladas: {len(orto_paths) - ortofotos_processadas - ortofotos_com_erro}")

if ortofotos_processadas > 0:
    print(f"\n🎉 Processamento concluído com sucesso!")
    print(f"📝 Verifique os arquivos .shp gerados em cada pasta de ortofoto")
else:
    print(f"\n⚠️ Nenhuma ortofoto foi processada com sucesso")
    print(f"🔧 Verifique os logs acima para identificar problemas")