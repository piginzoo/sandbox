import shapely,cv2,numpy as np
from shapely.geometry import  *
from shapely.ops import split


def test1():
    polygon = [[40, 20], [150, 50], [240, 130], [80, 120]]
    shapely_poly = Polygon(polygon)

    line = [(10, 20), (220, 180)]
    shapely_line = LineString(line)

    # intersection_line = list(shapely_poly.intersection(shapely_line).coords)
    # print(intersection_line.area)

    splited1,splited2 = split(shapely_poly,shapely_line)
    area1 = splited1.area
    area2 = splited2.area


    if area1>area2:
        big_split_polygon = splited1.exterior.coords
    else:
        big_split_polygon = splited2.exterior.coords
    # print(list(big_split_polygon))
    big_split_polygon = np.array(list(big_split_polygon),np.int32)

    image = np.full((400,400,3),255)

    image = cv2.polylines(image,[np.array(polygon)],True,(0,0,255),2)
    image = cv2.fillPoly(image,[big_split_polygon],(0,0,255))
    image = cv2.line(image,line[0],line[1],(255,0,0),2)
    return image


image = test1()

cv2.imwrite("../debug/test_shaply.jpg",image)