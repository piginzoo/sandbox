import os
import numpy as np
import random
from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

# def random_color(base_color=0, top_color=255):
#     noise_r = random.randint(base_color, top_color)
#     noise_g = random.randint(base_color, top_color)
#     noise_b = random.randint(base_color, top_color)
#     noise = np.array([noise_r, noise_g, noise_b])
#     font_color = noise.tolist()
#     return tuple(font_color)

def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return red, green, blue
    return red, green, blue, opacity    

# def random_color(base_color=0, top_color=255):
#     noise_r = random.randint(base_color, top_color)
#     noise_g = random.randint(base_color, top_color)
#     noise_b = random.randint(base_color, top_color)
#     noise = np.array([noise_r, noise_g, noise_b])
#     font_color = noise.tolist()
#     return tuple(font_color)


def random_background():
    background = random_color(100, 255, 255)
    image = Image.new('RGBA', (90,35), color=background)
    return image

def random_sin_fill(image):

    x = np.linspace(-10, 10, 1000)
    y = np.sin(x)
    color = random_color(100, 255)

    x_scale = random.randint(25,35)
    y_scale = random.randint(10,20)
    # 上曲线
    xy = np.asarray(
        np.stack((x * x_scale + random.randint(0, 90), 
            y * 15 - random.randint(2, 10)), axis=1), 
        dtype=int)

    xy = list(map(tuple, xy))
    Draw(image).polygon(xy, fill=color)

    # 下曲线
    x_scale = random.randint(25,35)
    y_scale = random.randint(10,20)
    xy = np.asarray(np.stack((x * x_scale + random.randint(0, 90), 
        y * y_scale + random.randint(37, 45)), axis=1), dtype=int)
    xy = list(map(tuple, xy))
    Draw(image).polygon(xy, fill=color)

    return image


def main():
    for i in range(100):
        image = random_background()
        image = random_sin_fill(image)
        image.save("data/test{}.png".format(i))


if __name__ == '__main__':
    main()