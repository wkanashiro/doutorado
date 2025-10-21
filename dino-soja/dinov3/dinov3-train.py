import os
import sys
import torch
from pathlib import Path
import subprocess

# CONFIGURAR PATHS
dinov3_path = "/home/lades/computer_vision/wesley/dino-soja/dinov3"
config_path = f"{dinov3_path}/dinov3/configs/train/dinov3_vit_small16_soja_256x256.yaml"
output_dir = "/home/lades/computer_vision/wesley/dino-soja/output-dinov3-soja"

def verify_environment():
    """Verificar ambiente e dependências"""
    
    print("🔍 Verificando ambiente...")
    
    # Verificar CUDA
    if not torch.cuda.is_available():
        raise RuntimeError("❌ CUDA não disponível!")
    
    gpu_name = torch.cuda.get_device_name(0)
    gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
    
    print(f"✅ GPU: {gpu_name}")
    print(f"✅ VRAM: {gpu_memory:.1f} GB")
    
    # Verificar DINOv3
    if not Path(dinov3_path).exists():
        raise FileNotFoundError(f"❌ DINOv3 não encontrado: {dinov3_path}")
    
    # Verificar config
    if not Path(config_path).exists():
        raise FileNotFoundError(f"❌ Config não encontrado: {config_path}")
    
    # Verificar dataset
    dataset_path = "/home/lades/computer_vision/wesley/dino-soja/dataset/teste-organizado-dinov3/"
    if not Path(dataset_path).exists():
        raise FileNotFoundError(f"❌ Dataset não encontrado: {dataset_path}")
    
    train_images = list(Path(dataset_path, "train", "soja").glob("*"))
    val_images = list(Path(dataset_path, "val", "soja").glob("*"))
    
    print(f"📊 Dataset: {len(train_images)} treino, {len(val_images)} validação")
    
    return gpu_memory

def adjust_config_for_gpu(gpu_memory):
    """Ajustar batch size baseado na VRAM"""
    
    if gpu_memory < 8:
        batch_size = 8
        print("⚠️ VRAM baixa, usando batch_size=8")
    elif gpu_memory < 16:
        batch_size = 16
        print("✅ Usando batch_size=16")
    else:
        batch_size = 32
        print("🚀 VRAM alta, usando batch_size=32")
    
    return batch_size

def start_training_updated():
    """Iniciar treinamento com estrutura DINOv3 oficial"""
    
    # Verificar ambiente
    gpu_memory = verify_environment()
    batch_size = adjust_config_for_gpu(gpu_memory)
    
    num_workers = 10 
    
    # Criar diretório de output
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Configurar ambiente Python
    env = os.environ.copy()
    env["PYTHONPATH"] = dinov3_path
    env["CUDA_VISIBLE_DEVICES"] = "0"

    dataset_path = "/home/lades/computer_vision/wesley/dino-soja/dataset/teste-organizado-dinov3/"

    cmd = [
        "python", "-m", "dinov3.train.train",
        "--config-file", config_path,
        "--output-dir", output_dir,
        # Parâmetros básicos mínimos
        f"train.batch_size_per_gpu={batch_size}",
        f"train.num_workers={num_workers}",
        f"train.dataset_path=Soja:root={dataset_path}:split=TRAIN:extra={dataset_path}/extra",
        
        # ========== ÉPOCAS ==========
        "optim.epochs=40",              # Treinamento mais longo
        "train.OFFICIAL_EPOCH_LENGTH=200",  # 200 iters/época = 20k iterações
        
        # ========== LEARNING RATE COM WARMUP ==========
        "schedules.lr.warmup_epochs=5",  # 5 épocas de warmup
        "schedules.lr.start=1.0e-06",    # Começar baixo
        "schedules.lr.peak=1.0e-04",     # LR máximo
        "schedules.lr.end=1.0e-06",      # Decair até quase zero
        
        # ========== WEIGHT DECAY ==========
        "schedules.weight_decay.warmup_epochs=5",
        "schedules.weight_decay.start=0.04",
        "schedules.weight_decay.peak=0.1",   # Aumentar para regularização
        "schedules.weight_decay.end=0.4",
        
        # ========== TEACHER TEMPERATURE ==========
        "schedules.teacher_temp.warmup_epochs=5",
        "schedules.teacher_temp.start=0.04",
        "schedules.teacher_temp.peak=0.04",
        "schedules.teacher_temp.end=0.07",
        
        # ========== MOMENTUM ==========
        "schedules.momentum.warmup_epochs=5",
        "schedules.momentum.start=0.996",
        "schedules.momentum.peak=0.996",
        "schedules.momentum.end=1.0",
        
        # ========== OTIMIZAÇÃO ==========
        "optim.clip_grad=3.0",
        "optim.optimizer=adamw",
        "optim.adamw_beta1=0.9",
        "optim.adamw_beta2=0.999",

        "train.saveckp_freq=5",         # Salvar a cada 5 épocas
        "checkpointing.period=500",     # Checkpoint intermediário a cada 500 iters
    ]
    
    print("Iniciando treinamento DINOv3 MÍNIMO...")
    print(f"Config: {config_path}")
    print(f"Batch size: {batch_size}")
    print(f"Épocas: 40")
    print(f"Output: {output_dir}")
    print(f"Comando: {' '.join(cmd)}")
    print("\n" + "="*60)

    # Executar treinamento
    try:
        result = subprocess.run(
            cmd,
            cwd=dinov3_path,
            env=env,
            check=True,
            capture_output=False  # Ver output direto
        )
        
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no treinamento: {e}")       
        raise
        
    except KeyboardInterrupt:
        print("\n Treinamento interrompido pelo usuário")
        raise

if __name__ == "__main__":
    start_training_updated()