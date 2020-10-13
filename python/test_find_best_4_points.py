import numpy as np
import random
import math



# 计算两个向量的向量积
# v1[0] --- x1, v1[1] --- y1
# v2[0] --- x2, v2[1] --- y2
def vec_prod(v1, v2):
    Z = v1[0] * v2[1] - v1[1] * v2[0]
    # 逆时针
    if Z > 0:
        return 1
    # 顺时针
    elif Z < 0:
        return -1
    # 三点共线
    else:
        return False


# 该函数对点序列按逆时针排序
# points[0] --- (x1, y1)
# points[1] --- (x2, y2)
# ...
def order_points(points):
    first = points[0]
    result = list()
    result.append(first)
    vectors = []

    for point in points[1:]:
        vectors.append((point[0] - first[0], point[1] - first[1]))

    vec_num = len(vectors)

    while vectors:
        if len(vectors) == 1:
            result.append((vectors[0][0] + first[0], vectors[0][1] + first[1]))
            vectors.pop()
        else:
            for i, v in enumerate(vectors):
                sign = list()

                for t in vectors[0:i] + vectors[i + 1:]:
                    sign.append(vec_prod(v, t))

                sign = set(sign)

                if False in sign:
                    return False

                # 都是逆时针了
                elif len(sign) == 1 and list(sign)[0] == 1:
                    result.append((v[0] + first[0], v[1] + first[1]))
                    vectors.pop(i)
                    break

            # 意思是，当在所有向量上查找一次了，还没有找到一条与所有向量的向量积的z都大于0的那个向量，就返回False
            # 这种情况只可能发生在非凸多边形中
            # 在凸多边形中不可能有这种情况
            # 因为在凸多边形中，起点相同的所有向量的夹角不会大于180度。
            if i == vec_num - 1 and len(vectors) == vec_num:
                return False
    return result


def fun_dist(line, point):
    x1 = line[0][0]
    x2 = line[1][0]
    y1 = line[0][1]
    y2 = line[1][1]

    x = point[0]
    y = point[1]

    # 需要判断边是否垂直x或y轴
    if x1 == x2:
        tmp = x
    elif y1 == y2:
        tmp = y
    else:
        tmp = (y1 - y2) / (x1 - x2) * (x - x1) + y1 - y

    return 1 if tmp > 0 else -1
# points必为排序后的点
# points[0] --- (x1, y1)
# points[1] --- (x2, y2)
# ...
def one_sied(points):
    result = list()
     # 遍历所有线
    for i in range(len(points)-1):
        line = points[i:i+2]
        res = list()
        # 对线之外的其他点进行判断
        for p in points[:i] + points[i+2:]:
            res.append(fun_dist(line, p))
        res = set(res)
        result.append(len(res))

    result = set(result)
    return True if len(result) == 1 else False

def convex(points):
    # 返回的点是逆时针排序的
    points = order_points(points)

    if points == False:
        return False

    result = one_sied(points)

    return result


def get_mean(points):
    x_mean = sum(xy[0] for xy in points) / len(points)
    y_mean = sum(xy[1] for xy in points) / len(points)
    return x_mean, y_mean


# points(list(4,2))
# 算法很简单，就是算出重心，然后求每个点到重心的角度，然后排序即可
def get_ordered_points(points):
    x_mean, y_mean = get_mean(points)

    def algo(xy):
        return math.atan2(xy[0] - x_mean, xy[1] - y_mean)

    sorted(points, key=algo)
    return points


# def get_ordered_points(p):
# 	p = np.array(p)
# 	mean = np.mean(p,axis=0)
# 	d = p-mean
# 	s = np.arctan2(d[:,0], d[:,1])
# 	return p[np.argsort(s),:]


width = 800
height = 600


# 找出4点的最优的组合，方便透射的效果

def distance(p1, p2):
    xy = p1[0] - p2[0]
    y = p1[1] - p2[1]
    return math.sqrt((xy ** 2) + (y ** 2))


all_points = []
for i in range(10):
    x = random.randint(1, width)
    y = random.randint(1, height)
    all_points.append([x, y])
# print(x,y)
print(all_points)

from itertools import combinations

compose_list = list(combinations(all_points, 4))
print(len(compose_list))

diagonals = []
for four_points in compose_list:
    
    ordered_4_points = order_points(four_points)
    if not ordered_4_points: continue

    result = one_sied(ordered_4_points)
    if result: continue

    print(ordered_4_points)
    if ordered_4_points:
	    l1 = distance(ordered_4_points[0], ordered_4_points[2])
	    l2 = distance(ordered_4_points[1], ordered_4_points[3])
	    l = max(l1, l2)
	    diagonals.append(abs(l1 - l2) / l)

import numpy as np
import cv2

diagonals = np.array(diagonals)
sorted_indexs = diagonals.argsort()

top_10 = sorted_indexs[:1]

image = np.full((height, width, 3), 255)
for i in top_10:
    pos = np.array(compose_list[i])
    image = cv2.polylines(image, [pos], True, (0, 0, 255), 2)

for p in all_points:
    image = cv2.circle(image, (p[0], p[1]), 1, (255, 0, 0), 10)

cv2.imwrite("test.jpg", image)






