import numpy as np
import cv2
import shapely
import geopandas as gpd

def to_numpy2(transform):
    return np.array([transform.a,
                     transform.b,
                     transform.c,
                     transform.d,
                     transform.e,
                     transform.f, 0, 0, 1], dtype='float64').reshape((3, 3))


def xy_np(transform, rows, cols, min_x, min_y, offset='center'):
    if isinstance(rows, int) and isinstance(cols, int):
        pts = np.array([[rows+min_y, cols+min_x, 1]]).T
    else:
        assert len(rows) == len(cols)
        pts = np.ones((3, len(rows)), dtype=int)
        pts[0] = rows + min_y
        pts[1] = cols + min_x
    if offset == 'center':
        coff, roff = (0.5, 0.5)
    elif offset == 'ul':
        coff, roff = (0, 0)
    elif offset == 'ur':
        coff, roff = (1, 0)
    elif offset == 'll':
        coff, roff = (0, 1)
    elif offset == 'lr':
        coff, roff = (1, 1)
    else:
        raise ValueError("Invalid offset")
    _transnp = to_numpy2(transform)
    _translt = to_numpy2(transform.translation(coff, roff))
    locs = _transnp @ _translt @ pts
    lat, lon = locs[0].tolist(), locs[1].tolist()
    coords = [(lat[i], lon[i]) for i in range(len(lat))]
    return coords

def polygons_from_binary_image(img, transform, crs, min_x=0, min_y=0, min_area=5):

    assert isinstance(img, np.ndarray), 'img deve ser um numpy array'

    unique_values = np.unique(img)

    new_geo_data_frame = {"geometry": [], 'CLASSE': []}

    for cat in unique_values:
        if cat == 0:
            continue

        img_ = img.copy()
        img_[img_ != cat] = 0
        img_[img_ != 0] = 1

        contours, hierarchy = cv2.findContours(img_, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        
        categ = cat

        interiors = [xy_np(transform, contour[:, 0, 0], contour[:, 0, 1], min_x, min_y)
                     for c, contour in enumerate(contours) if hierarchy[0][c][3] != -1]
        index = [
            hierarchy[0][c][3]
            for c, contour in enumerate(contours)
            if hierarchy[0][c][3] != -1
        ]

        for c, contour in enumerate(contours):
            if hierarchy[0][c][3] == -1:
                if cv2.contourArea(contour) < min_area:
                    continue
                exterior = xy_np(
                    transform, contour[:, 0, 0], contour[:, 0, 1], min_x, min_y)
                interior = [hole for h, hole in enumerate(
                    interiors) if index[h] == c]
                if len(exterior) <= 3:
                    continue
                poly = shapely.geometry.polygon.Polygon(exterior, interior)
                new_geo_data_frame["geometry"].append(poly)
                new_geo_data_frame["CLASSE"].append(categ)

    gdf1 = gpd.GeoDataFrame.from_dict(new_geo_data_frame, geometry="geometry", crs=crs)

    return gdf1