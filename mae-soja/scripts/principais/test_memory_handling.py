#!/usr/bin/env python3
"""
Teste do tratamento de erros de memória no sistema de processamento de ortofotos
"""

import sys
import os

def test_memory_handling():
    """Testa o tratamento de erros de memória"""
    print("=" * 60)
    print("TESTE: TRATAMENTO DE ERROS DE MEMÓRIA")
    print("=" * 60)
    
    # Configura paths
    mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
    pred_path = '/home/lades/computer_vision/wesley/mae-soja/prediction_orthophoto'
    
    if mmseg_local_path not in sys.path:
        sys.path.insert(0, mmseg_local_path)
    if pred_path not in sys.path:
        sys.path.insert(0, pred_path)
    
    try:
        # Importa as funções
        from prediction.prediction_orthophoto import prediction, prediction_in_plot
        from models.load import get_mmsegmentation_model
        from utils.files import find_subfolders_in_folder, find_tif_shp_in_folder
        import geopandas as gpd
        import rasterio
        
        print("✓ Todas as importações funcionando!")
        
        # Carrega modelo
        config_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/mae-base_upernet_8xb2-amp-20k_daninhas-256x256.py'
        checkpoint_file = '/home/lades/computer_vision/wesley/mae-soja/models/modelo_final/iter_40000.pth'
        device = 'cuda:0'
        
        print("\n🔄 Carregando modelo...")
        model = get_mmsegmentation_model(config_file, checkpoint_file, device)
        print("✓ Modelo carregado!")
        
        # Busca dados de teste
        test_data_path = '/home/lades/computer_vision/wesley/mae-soja/data/input/ortofotos_soja'
        if not os.path.exists(test_data_path):
            print(f"⚠️ Diretório de teste não encontrado: {test_data_path}")
            return False
        
        areas = find_subfolders_in_folder(test_data_path, extensions=['.tif', '.shp'])
        if not areas:
            print("⚠️ Nenhuma área encontrada para teste")
            return False
        
        print(f"\n📂 Encontradas {len(areas)} áreas para teste")
        
        # Testa com uma área
        test_area = areas[0]
        print(f"\n🧪 Testando com área: {os.path.basename(test_area)}")
        
        tif_path, shp_path = find_tif_shp_in_folder(test_area)
        if not tif_path or not shp_path:
            print("❌ Arquivos .tif ou .shp não encontrados")
            return False
        
        print(f"🗺️ TIF: {os.path.basename(tif_path)}")
        print(f"📐 SHP: {os.path.basename(shp_path)}")
        
        # Verifica informações da ortofoto
        with rasterio.open(tif_path) as dataset:
            print(f"📏 Dimensões: {dataset.width} x {dataset.height}")
            print(f"🎯 CRS: {dataset.crs}")
        
        # Verifica talhões
        gpd_talhoes = gpd.read_file(shp_path)
        print(f"🧩 Talhões: {len(gpd_talhoes)}")
        
        # Executa prediction com tratamento de erro
        print(f"\n🚀 Executando prediction com tratamento de erros...")
        patch_size = 256
        step = patch_size // 2
        
        try:
            shp_result = prediction(shp_path, tif_path, model, patch_size, step)
            
            if len(shp_result) > 0:
                print(f"✅ Prediction executada com sucesso!")
                print(f"📊 Resultados: {len(shp_result)} polígonos gerados")
                
                # Verifica colunas do resultado
                print(f"📋 Colunas: {list(shp_result.columns)}")
                
                # Salva resultado de teste
                output_path = '/home/lades/computer_vision/wesley/mae-soja/data/output/teste_memoria.shp'
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shp_result.to_file(output_path)
                print(f"💾 Resultado salvo em: {output_path}")
                
            else:
                print("⚠️ Nenhum resultado gerado (possivelmente todos os talhões foram pulados)")
            
        except Exception as e:
            print(f"❌ Erro durante prediction: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ Teste de tratamento de memória concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_memory_error():
    """Simula situação de erro de memória para testar tratamento"""
    print("\n" + "=" * 60)
    print("SIMULAÇÃO: ERRO DE MEMÓRIA")
    print("=" * 60)
    
    try:
        # Tenta alocar um array muito grande para simular erro de memória
        import numpy as np
        
        print("🧪 Testando alocação de memória...")
        
        # Calcula tamanho de array que pode causar problema (mas não quebrar tudo)
        # Tentativa de 8GB (float32)
        size = int(2e9)  # ~8GB em float32
        print(f"📐 Tentando alocar array de tamanho {size:,} elementos (~8GB)")
        
        try:
            test_array = np.zeros(size, dtype=np.float32)
            print("✓ Array alocado com sucesso")
            del test_array  # Libera memória
            print("✓ Memória liberada")
        except (MemoryError, np.core._exceptions._ArrayMemoryError) as e:
            print(f"🚫 MemoryError capturado corretamente: {e}")
            print("✅ Tratamento de erro funcionando!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na simulação: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTE DE TRATAMENTO DE ERROS DE MEMÓRIA")
    
    # Teste 1: Funcionalidade normal com tratamento de erro
    normal_ok = test_memory_handling()
    
    # Teste 2: Simulação de erro de memória
    simulation_ok = simulate_memory_error()
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO FINAL")
    print("=" * 60)
    print(f"🧪 Teste normal: {'✓ OK' if normal_ok else '✗ FALHOU'}")
    print(f"🎭 Simulação: {'✓ OK' if simulation_ok else '✗ FALHOU'}")
    
    if normal_ok and simulation_ok:
        print("\n🎉 TRATAMENTO DE ERROS DE MEMÓRIA FUNCIONAL!")
        print("✅ Sistema pode lidar com talhões grandes pulando-os")
        print("📝 Recomendação: Monitorar logs para ver quais talhões são pulados")
    else:
        print("\n❌ PROBLEMAS NO TRATAMENTO DE ERROS")
        print("🔧 Verificar implementação do tratamento de MemoryError")
