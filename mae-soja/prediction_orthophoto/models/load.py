def get_mmsegmentation_model(config_file, checkpoint_file, device):
    import sys
    import os
    
    # Garante que o mmsegmentation local está no path
    mmseg_local_path = '/home/lades/computer_vision/wesley/mae-soja/mmsegmentation'
    if mmseg_local_path not in sys.path:
        sys.path.insert(0, mmseg_local_path)
    
    # Importa do mmsegmentation local (compatível com mmcv 2.0.0)
    from mmseg.apis import init_model
    print("✓ Carregando modelo com mmsegmentation LOCAL")
    
    # build the model from a config file and a checkpoint file
    model = init_model(config_file, checkpoint_file, device=device)
    return model