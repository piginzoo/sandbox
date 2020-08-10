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

poly1= \
[[ 417, 3968], [2472.75, 4102.6561135371185], [2472.75, 4121.71615720524], [ 195, 3883]]
poly2 = \
[[ 535, 3964],
 [ 423, 3964],
 [ 423, 3915],
 [ 535, 3915]]

poly1= [[208, 736], [518.0, 736.0], [518.0, 752.0],[616, 752]]
poly2 = [[563,752],[417,752],[417,741],[563,741]]
image = np.full((4200,4200,3),255)
image = cv2.polylines(image,[np.array(poly1,np.int32).reshape(4,2)],True,(0,0,255),2)
image = cv2.polylines(image,[np.array(poly2,np.int32).reshape(4,2)],True,(255,0,0),3)
cv2.imwrite("../debug/test_shapely2.jpg",image)

# poly1 = Polygon(poly1)
# poly2 = Polygon(poly2)
# print(poly1.intersection(poly2).area)


