import os

def find_subfolders_in_folder(path, extensions=None):
    if extensions is None:
        return [f.path for f in os.scandir(path) if f.is_dir()]
    else:
        # Retornar a subpasta se dentro dela tiver pelo menos um arquivo com cada extensão na lista extensions
        return [f.path for f in os.scandir(path) if f.is_dir() and all([find_file_in_folder(f.path, ext) is not None for ext in extensions])]
        
def find_file_in_folder(path, extension):
    filenames = [f for f in os.listdir(path) if f.endswith(extension)]
    return os.path.join(path, filenames[0]) if len(filenames) > 0 else None

def find_tif_shp_in_folder(path):
    tif_path = find_file_in_folder(path, '.tif')
    shp_path = find_file_in_folder(path, '.shp')

    return tif_path, shp_path