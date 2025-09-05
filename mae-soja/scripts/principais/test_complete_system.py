#!/usr/bin/env python3
"""
Teste completo do sistema com mmsegmentation local
"""

import sys
import os

def test_local_mmseg():
    """Testa mmsegmentation local com mmcv 2.0.0"""
    print("=" * 60)
    print("TESTE: MMSEGMENTATION LOCAL + MMCV 2.0.0")
    print("=" * 60)
    
    # Configura path para mmsegmentation local
    mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
    if mmseg_local_path not in sys.path:
        sys.path.insert(0, mmseg_local_path)
        print(f"✓ Adicionado ao path: {mmseg_local_path}")
    
    try:
        # Testa importações
        import mmcv
        import mmseg
        from mmseg.apis import init_model, inference_model
        
        print(f"✓ mmcv version: {mmcv.__version__}")
        print(f"✓ mmseg version: {mmseg.__version__}")
        print(f"✓ mmseg localização: {mmseg.__file__}")
        print("✓ Todas as importações funcionando!")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro nas importações: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_loading():
    """Testa carregamento do modelo"""
    print("\n" + "=" * 60)
    print("TESTE: CARREGAMENTO DO MODELO")
    print("=" * 60)
    
    try:
        # Adiciona path do prediction_orthophoto
        pred_path = '/home/lades/computer_vision/wesley/mae-soja/prediction_orthophoto'
        if pred_path not in sys.path:
            sys.path.insert(0, pred_path)
        
        from models.load import get_mmsegmentation_model
        
        config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
        checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
        device = 'cuda:0'
        
        print(f"📄 Config: {os.path.basename(config_file)}")
        print(f"📦 Checkpoint: {os.path.basename(checkpoint_file)}")
        print(f"🖥️ Device: {device}")
        
        print("\n🔄 Carregando modelo...")
        model = get_mmsegmentation_model(config_file, checkpoint_file, device)
        print("✓ Modelo carregado com sucesso!")
        
        # Informações do modelo
        print(f"🤖 Tipo do modelo: {type(model)}")
        if hasattr(model, 'cfg'):
            print(f"📋 Config do modelo disponível: ✓")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no carregamento: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prediction_function():
    """Testa a função de prediction"""
    print("\n" + "=" * 60)
    print("TESTE: FUNÇÃO PREDICTION")
    print("=" * 60)
    
    try:
        # Adiciona paths necessários
        mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
        pred_path = '/home/lades/computer_vision/wesley/mae-soja/prediction_orthophoto'
        
        if mmseg_local_path not in sys.path:
            sys.path.insert(0, mmseg_local_path)
        if pred_path not in sys.path:
            sys.path.insert(0, pred_path)
        
        # Testa importação da função prediction
        from prediction.prediction_orthophoto import prediction
        print("✓ Função prediction importada com sucesso!")
        
        # Verifica se há dados de teste
        test_data_path = '/home/lades/computer_vision/wesley/mae-soja/data/input/ortofotos_soja'
        if os.path.exists(test_data_path):
            from utils.files import find_subfolders_in_folder
            areas = find_subfolders_in_folder(test_data_path, extensions=['.tif', '.shp'])
            print(f"📂 Encontradas {len(areas)} áreas de teste")
        else:
            print("⚠️ Diretório de dados de teste não encontrado")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro na função prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TESTE COMPLETO DO SISTEMA")
    
    # Teste 1: Importações
    imports_ok = test_local_mmseg()
    
    # Teste 2: Carregamento do modelo
    model_ok = False
    if imports_ok:
        model_ok = test_model_loading()
    
    # Teste 3: Função prediction
    prediction_ok = False
    if imports_ok:
        prediction_ok = test_prediction_function()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    print(f"📦 Importações: {'✓ OK' if imports_ok else '✗ FALHOU'}")
    print(f"🤖 Modelo: {'✓ OK' if model_ok else '✗ FALHOU'}")
    print(f"🔮 Prediction: {'✓ OK' if prediction_ok else '✗ FALHOU'}")
    
    if imports_ok and model_ok and prediction_ok:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("✅ Pode executar prediction_mmsegmentation.py")
    elif imports_ok and prediction_ok:
        print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        print("📝 Importações e prediction OK, mas modelo pode ter problemas")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS")
        print("🔧 Verifique as configurações de mmcv e mmsegmentation")
