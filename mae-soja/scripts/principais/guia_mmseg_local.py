#!/usr/bin/env python3
"""
GUIA: Como usar mmsegmentation LOCAL ao invés do ambiente

Este guia mostra como configurar seu script para usar o mmsegmentation
do diretório físico do projeto ao invés da instalação do ambiente.
"""

import sys
import os

def setup_local_mmsegmentation():
    """
    Configura o sys.path para usar o mmsegmentation local.
    
    IMPORTANTE: Esta função deve ser chamada ANTES de qualquer
    importação relacionada ao mmsegmentation.
    """
    # Caminho para o diretório mmsegmentation local
    mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
    
    # Verifica se o diretório existe
    if not os.path.exists(mmseg_local_path):
        print(f"⚠️ Diretório mmsegmentation local não encontrado: {mmseg_local_path}")
        return False
    
    # Adiciona ao início do sys.path (prioridade máxima)
    if mmseg_local_path not in sys.path:
        sys.path.insert(0, mmseg_local_path)
        print(f"✓ mmsegmentation local adicionado ao path: {mmseg_local_path}")
        return True
    else:
        print(f"✓ mmsegmentation local já está no path")
        return True

def get_mmsegmentation_model_local(config_file, checkpoint_file, device):
    """
    Versão modificada da função de carregamento que usa mmsegmentation local.
    """
    # Configura o path local ANTES de importar
    if not setup_local_mmsegmentation():
        raise ImportError("Não foi possível configurar mmsegmentation local")
    
    try:
        # Importa do mmsegmentation local
        from mmseg.apis import init_model
        print("✓ Usando mmsegmentation LOCAL")
        
        # Verifica localização
        import mmseg
        print(f"📍 mmseg localizado em: {mmseg.__file__}")
        
    except ImportError as e:
        print(f"✗ Erro ao importar do mmsegmentation local: {e}")
        raise
    
    # Carrega o modelo
    print("🔄 Carregando modelo...")
    model = init_model(config_file, checkpoint_file, device=device)
    print("✓ Modelo carregado com sucesso!")
    
    return model

# ============================================================================
# EXEMPLOS DE USO
# ============================================================================

def exemplo_script_simples():
    """
    Exemplo 1: Script simples usando mmsegmentation local
    """
    print("=" * 60)
    print("EXEMPLO 1: Script simples")
    print("=" * 60)
    
    # IMPORTANTE: Configurar ANTES de qualquer importação
    setup_local_mmsegmentation()
    
    # Agora pode importar normalmente
    from mmseg.apis import init_model
    
    # Seus parâmetros
    config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
    checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
    device = 'cuda:0'
    
    # Carrega modelo
    model = init_model(config_file, checkpoint_file, device=device)
    print("✓ Modelo carregado usando mmsegmentation local!")

def exemplo_modificar_prediction_mmsegmentation():
    """
    Exemplo 2: Como modificar o prediction_mmsegmentation.py
    """
    print("=" * 60) 
    print("EXEMPLO 2: Modificando prediction_mmsegmentation.py")
    print("=" * 60)
    
    script_content = '''
import sys
import os

# ADICIONAR ESTAS LINHAS NO INÍCIO DO SCRIPT (ANTES DE QUALQUER IMPORTAÇÃO)
# ========================================================================
mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
if mmseg_local_path not in sys.path:
    sys.path.insert(0, mmseg_local_path)
    print(f"✓ Usando mmsegmentation local: {mmseg_local_path}")
# ========================================================================

# Agora as importações normais
from models.load import get_mmsegmentation_model
from utils.files import find_subfolders_in_folder, find_tif_shp_in_folder
from prediction.prediction_orthophoto import prediction

# Resto do script permanece igual...
'''
    
    print("Código para adicionar no início do prediction_mmsegmentation.py:")
    print(script_content)

def exemplo_criar_funcao_robusta():
    """
    Exemplo 3: Função robusta que tenta local primeiro, depois ambiente
    """
    print("=" * 60)
    print("EXEMPLO 3: Função robusta com fallback")
    print("=" * 60)
    
    function_content = '''
def get_model_with_fallback(config_file, checkpoint_file, device):
    """
    Tenta usar mmsegmentation local primeiro, depois ambiente como fallback.
    """
    import sys
    import os
    
    # Tentativa 1: mmsegmentation local
    mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
    
    if os.path.exists(mmseg_local_path):
        if mmseg_local_path not in sys.path:
            sys.path.insert(0, mmseg_local_path)
        
        try:
            from mmseg.apis import init_model
            print("✓ Usando mmsegmentation LOCAL")
            model = init_model(config_file, checkpoint_file, device=device)
            return model
        except Exception as e:
            print(f"⚠️ Falha com mmsegmentation local: {e}")
            # Remove do path para tentar ambiente
            if mmseg_local_path in sys.path:
                sys.path.remove(mmseg_local_path)
    
    # Tentativa 2: mmsegmentation do ambiente
    try:
        # Força reimportação
        if 'mmseg' in sys.modules:
            del sys.modules['mmseg']
        if 'mmseg.apis' in sys.modules:
            del sys.modules['mmseg.apis']
            
        from mmseg.apis import init_model
        print("✓ Usando mmsegmentation do AMBIENTE")
        model = init_model(config_file, checkpoint_file, device=device)
        return model
    except Exception as e:
        print(f"✗ Falha com mmsegmentation do ambiente: {e}")
        raise Exception("Não foi possível carregar mmsegmentation nem local nem do ambiente")
'''
    
    print("Função robusta com fallback:")
    print(function_content)

if __name__ == "__main__":
    print("🎯 GUIA: USANDO MMSEGMENTATION LOCAL")
    print("\nEscolha um exemplo:")
    print("1. Script simples")
    print("2. Modificar prediction_mmsegmentation.py") 
    print("3. Função robusta com fallback")
    
    try:
        choice = input("\nEscolha (1-3): ").strip()
        
        if choice == "1":
            exemplo_script_simples()
        elif choice == "2":
            exemplo_modificar_prediction_mmsegmentation()
        elif choice == "3":
            exemplo_criar_funcao_robusta()
        else:
            print("Escolha inválida. Mostrando todos os exemplos:")
            exemplo_script_simples()
            exemplo_modificar_prediction_mmsegmentation()
            exemplo_criar_funcao_robusta()
            
    except KeyboardInterrupt:
        print("\n\nMostrando todos os exemplos:")
        exemplo_script_simples()
        exemplo_modificar_prediction_mmsegmentation()
        exemplo_criar_funcao_robusta()
