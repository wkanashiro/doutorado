import cv2
import numpy as np

def get_img(geo_data_frame, func_latlon_xy, index, min_img_size):
    geo_data_frame = geo_data_frame.explode(ignore_index=True)

    bounds = geo_data_frame.iloc[[index]].bounds
    min_lat = bounds["minx"].min()
    max_lon = bounds["miny"].min()
    max_lat = bounds["maxx"].max()
    min_lon = bounds["maxy"].max()

    min_x, min_y = func_latlon_xy(min_lat, min_lon)
    max_x, max_y = func_latlon_xy(max_lat, max_lon)

    # assert max_x-min_x > 0 and max_y-min_y > 0, 'Erro de dimensoes'
    if not ((max_x - min_x > 0) and (max_y - min_y > 0)):
        print("Talhão vazio!")
        return None

    if max_x - min_x < min_img_size:
        max_x = min_x + min_img_size
    if max_y - min_y < min_img_size:
        max_y = min_y + min_img_size

    min_x, min_y, max_x, max_y = int(min_x), int(min_y), int(max_x), int(max_y)
    width, height = int(max_x - min_x), int(max_y - min_y)

    # Criar uma imagem em branco usando OpenCV
    image = np.zeros((width, height), dtype=np.uint8)

    geometry = geo_data_frame.geometry.iloc[index]


    pts = np.array(
        [
            func_latlon_xy(point[0], point[1])
            for point in geometry.exterior.coords[:]
        ],
        np.int32,
    )[:, ::-1]
    pts = pts - np.array([min_y, min_x])
            
    cv2.fillPoly(image, [pts], 1)
    for interior in geometry.interiors:
        pts = np.array(
            [
                func_latlon_xy(point[0], point[1])
                for point in interior.coords[:]
            ],
            np.int32,
        )[:, ::-1]
        pts = pts - np.array([min_y, min_x])
        cv2.fillPoly(image, [pts], 0)

    return (
        image,
        (min_x, min_y, max_x, max_y),
        (min_lat, max_lat, min_lon, max_lon),
    )