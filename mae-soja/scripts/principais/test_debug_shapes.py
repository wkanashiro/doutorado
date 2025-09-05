#!/usr/bin/env python3
"""
Script de teste para debug do problema de shapes
"""

import sys
import os
import traceback

# Configuração de paths
mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
pred_path = '/home/lades/computer_vision/wesley/mae-soja/prediction_orthophoto'

if mmseg_local_path not in sys.path:
    sys.path.insert(0, mmseg_local_path)
if pred_path not in sys.path:
    sys.path.insert(0, pred_path)

def test_prediction_debug():
    """Teste com debug detalhado"""
    try:
        print("=" * 60)
        print("TESTE DEBUG - PROBLEMA DE SHAPES")
        print("=" * 60)
        
        from models.load import get_mmsegmentation_model
        from utils.files import find_subfolders_in_folder, find_tif_shp_in_folder
        from prediction.prediction_orthophoto import prediction
        
        # Configuração
        config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
        checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
        device = 'cuda:0'
        
        print("🔄 Carregando modelo...")
        model = get_mmsegmentation_model(config_file, checkpoint_file, device)
        print("✓ Modelo carregado com sucesso")
        
        # Busca dados
        path_folder = '/home/lades/computer_vision/wesley/mae-soja/data/input/ortofotos_soja/'
        orto_paths = find_subfolders_in_folder(path_folder, extensions=['.tif', '.shp'])
        print(f"📂 Encontradas {len(orto_paths)} ortofotos")
        
        if len(orto_paths) == 0:
            print("❌ Nenhuma ortofoto encontrada!")
            return
        
        # Testa primeira ortofoto
        orto_path = orto_paths[0]
        print(f"🧪 Testando: {os.path.basename(orto_path)}")
        
        tif_path, shp_path = find_tif_shp_in_folder(orto_path)
        if not tif_path or not shp_path:
            print("❌ Arquivos TIF ou SHP não encontrados!")
            return
            
        print(f"📄 TIF: {os.path.basename(tif_path)}")
        print(f"📍 SHP: {os.path.basename(shp_path)}")
        
        # Executa predição
        print("\n🔮 Iniciando predição...")
        shp_result = prediction(shp_path, tif_path, model, 256, 128)
        
        print(f"✅ Predição concluída!")
        print(f"📊 Resultado: {len(shp_result)} detecções")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO CAPTURADO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(f"\n📋 Traceback completo:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_prediction_debug()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTE PASSOU! O problema foi corrigido.")
    else:
        print("🔧 TESTE FALHOU. Verifique o erro acima.")
    print("=" * 60)
