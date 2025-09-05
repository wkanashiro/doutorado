#!/usr/bin/env python3
"""
Script para testar o uso do mmsegmentation local vs ambiente
"""

import sys
import os

def test_mmseg_local():
    """Testa o carregamento do mmsegmentation local"""
    print("=" * 60)
    print("TESTE: MMSEGMENTATION LOCAL")
    print("=" * 60)
    
    # Caminho para o mmsegmentation local
    mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
    
    print(f"📁 Verificando diretório local: {mmseg_local_path}")
    if not os.path.exists(mmseg_local_path):
        print(f"✗ Diretório não encontrado: {mmseg_local_path}")
        return False
    
    # Adiciona ao path
    if mmseg_local_path not in sys.path:
        sys.path.insert(0, mmseg_local_path)
        print(f"✓ Adicionado ao sys.path: {mmseg_local_path}")
    
    try:
        # Tenta importar do local
        import mmseg
        print(f"✓ mmseg importado do local")
        print(f"📍 Localização: {mmseg.__file__}")
        print(f"🔖 Versão: {mmseg.__version__}")
        
        # Testa a importação específica
        from mmseg.apis import init_model
        print(f"✓ init_model importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao importar mmsegmentation local: {e}")
        return False

def test_mmseg_environment():
    """Testa o carregamento do mmsegmentation do ambiente"""
    print("\n" + "=" * 60)
    print("TESTE: MMSEGMENTATION DO AMBIENTE")
    print("=" * 60)
    
    # Remove paths locais se existirem
    mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
    if mmseg_local_path in sys.path:
        sys.path.remove(mmseg_local_path)
        print(f"🗑️ Removido do sys.path: {mmseg_local_path}")
    
    try:
        # Força reimportação
        if 'mmseg' in sys.modules:
            del sys.modules['mmseg']
        if 'mmseg.apis' in sys.modules:
            del sys.modules['mmseg.apis']
            
        import mmseg
        print(f"✓ mmseg importado do ambiente")
        print(f"📍 Localização: {mmseg.__file__}")
        print(f"🔖 Versão: {mmseg.__version__}")
        
        from mmseg.apis import init_model
        print(f"✓ init_model importado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao importar mmsegmentation do ambiente: {e}")
        return False

def test_model_loading():
    """Testa o carregamento do modelo"""
    print("\n" + "=" * 60)
    print("TESTE: CARREGAMENTO DO MODELO")
    print("=" * 60)
    
    config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
    checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
    device = 'cuda:0'
    
    # Verifica se os arquivos existem
    if not os.path.exists(config_file):
        print(f"✗ Config file não encontrado: {config_file}")
        return False
        
    if not os.path.exists(checkpoint_file):
        print(f"✗ Checkpoint não encontrado: {checkpoint_file}")
        return False
    
    print(f"✓ Config file encontrado")
    print(f"✓ Checkpoint encontrado")
    
    try:
        # Importa função de carregamento
        sys.path.insert(0, '/home/lades/computer_vision/wesley/mae-soja/prediction_orthophoto')
        from models.load import get_mmsegmentation_model
        
        print("🔄 Carregando modelo...")
        model = get_mmsegmentation_model(config_file, checkpoint_file, device)
        print("✓ Modelo carregado com sucesso!")
        return True
        
    except Exception as e:
        print(f"✗ Erro ao carregar modelo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TESTANDO CONFIGURAÇÕES DO MMSEGMENTATION")
    
    # Teste 1: mmsegmentation local
    local_ok = test_mmseg_local()
    
    # Teste 2: mmsegmentation do ambiente  
    env_ok = test_mmseg_environment()
    
    # Teste 3: carregamento do modelo
    model_ok = test_model_loading()
    
    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"📦 Mmsegmentation local: {'✓ OK' if local_ok else '✗ FALHOU'}")
    print(f"🌍 Mmsegmentation ambiente: {'✓ OK' if env_ok else '✗ FALHOU'}")
    print(f"🤖 Carregamento do modelo: {'✓ OK' if model_ok else '✗ FALHOU'}")
    
    if local_ok:
        print("\n🎉 RECOMENDAÇÃO: Usar mmsegmentation LOCAL")
    elif env_ok:
        print("\n⚠️ RECOMENDAÇÃO: Usar mmsegmentation do AMBIENTE")
    else:
        print("\n❌ PROBLEMA: Nenhuma configuração funcionou!")
