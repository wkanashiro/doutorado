import numpy as np
from rasterio.windows import Window

def get_image_patch(dataset, x, y, w, h):
    nc = 3
    img = np.zeros((h, w, nc), dtype=np.uint8)
    
    for i in range(nc):
        band = dataset.read(i+1, window=Window(y, x, w, h))
        nw, nh = band.shape[0], band.shape[1]
        if nw == 0 or nh == 0:
            return None
        img[0:nw, 0:nh, i] = band
    return img