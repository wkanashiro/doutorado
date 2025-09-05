#!/usr/bin/env python3
"""
Teste simples de compatibilidade mmcv + mmsegmentation
"""

def test_basic_imports():
    """Testa importações básicas"""
    try:
        print("🔍 Testando importações básicas...")
        
        import mmcv
        print(f"✓ mmcv version: {mmcv.__version__}")
        
        import mmseg
        print(f"✓ mmseg version: {mmseg.__version__}")
        
        from mmseg.apis import init_model, inference_model
        print("✓ init_model e inference_model importados!")
        
        return True
    except Exception as e:
        print(f"✗ Erro nas importações: {e}")
        return False

def test_model_loading():
    """Testa carregamento do modelo"""
    try:
        print("\n🤖 Testando carregamento do modelo...")
        
        from mmseg.apis import init_model
        
        config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
        checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
        device = 'cuda:0'
        
        print(f"📄 Config: {config_file}")
        print(f"📦 Checkpoint: {checkpoint_file}")
        
        model = init_model(config_file, checkpoint_file, device=device)
        print("✓ Modelo carregado com sucesso!")
        return True
        
    except Exception as e:
        print(f"✗ Erro no carregamento: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE RÁPIDO DE COMPATIBILIDADE")
    print("=" * 60)
    
    imports_ok = test_basic_imports()
    
    if imports_ok:
        model_ok = test_model_loading()
    else:
        model_ok = False
    
    print("\n" + "=" * 60)
    print("RESULTADO FINAL")
    print("=" * 60)
    if imports_ok and model_ok:
        print("🎉 TUDO FUNCIONANDO!")
        print("Pode executar o prediction_mmsegmentation.py")
    else:
        print("❌ AINDA HÁ PROBLEMAS")
        print("Verifique as versões de mmcv e mmsegmentation")
