import cv2,numpy as np
from shapely.geometry import *


poly1= \
[[2495,289],
 [4000,289],
 [10000,338],
 [2621,338]]

poly2 = \
[[2599,365],
 [2599,315],
 [2647,315],
 [2647,365]]
image = np.full((4100,4000,3),255)
image = cv2.polylines(image,[np.array(poly1).reshape(4,2)],True,(0,0,255),2)
image = cv2.polylines(image,[np.array(poly2).reshape(4,2)],True,(255,0,0),3)
cv2.imwrite("../debug/test_shapely2.jpg",image)

poly1 = Polygon(poly1)
poly2 = Polygon(poly2)
print(poly1.intersection(poly2).area)


