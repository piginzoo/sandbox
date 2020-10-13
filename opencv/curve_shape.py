from PIL import Image,ImageDraw,ImageFont
import numpy as np
import cv2,random,math
import io
import matplotlib.pyplot as plt

IMAGE_WIDTH = 90*3
IMAGE_HEIGHT = 35*3
NUM=10
LINE_WEIGHT=int(IMAGE_HEIGHT*2/4)


def save():
    plt.figure()
    plt.plot([1, 2])
    plt.title("test")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    im = Image.open(buf)
    im.show()
    buf.close()

def wave2():
    X = np.linspace(-2*np.pi, 2*np.pi, 256, endpoint=True)
    sin = np.sin(X)
    sin = 0.1*sin

    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.plot(X, sin, "b-", lw=10)
    plt.savefig('./test.jpg')


def wave3():
    from skimage import draw, data
    plt.gca().set_axis_off()
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0,hspace=0, wspace=0)
    plt.margins(0, 0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    lines = get_wave()
    for i in range(len(lines)-1):
        p1 =  lines[i]
        p2 = lines[i+1]
        rr, cc = draw.line(p1[0],p1[1],p2[0],p2[1])  # 表示从（1，150）到（470，450）连一条线，返回线上所有的像素点坐标[rr,cc]
    plt.imshow(img, plt.cm.gray)
    plt.savefig('./test.jpg')

def get_lines():
    xs = np.linspace(0,IMAGE_WIDTH,num=NUM,dtype=int)
    y1=random.randint(int(IMAGE_HEIGHT/2),int(IMAGE_HEIGHT*5/4))
    y2=random.randint(-int(IMAGE_HEIGHT/4),int(IMAGE_HEIGHT/2))
    ys = np.linspace(y1,y2,num=NUM,dtype=int)
    lines = []
    for x,y in zip(xs,ys):
        lines.append((x,y))
    return lines

def get_wave():
    xs = np.linspace(0,math.pi*2,num=NUM).tolist()
    ys = [ int(math.sin(x)*0.5*IMAGE_HEIGHT/2 + IMAGE_HEIGHT/2) for x in xs]

    xs = np.linspace(0,IMAGE_WIDTH,num=NUM,dtype=int)
    lines = []
    for x,y in zip(xs,ys):
        lines.append((x,y))
    return lines

def wave():
    image = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), color=(255,255,255))
    draw = ImageDraw.Draw(image)
    lines = get_wave()
    draw.line(lines, fill=(0, 255, 0),width=LINE_WEIGHT)

    # draw.line([(-50,y1),(int(IMAGE_WIDTH/2),y2),(IMAGE_WIDTH+50,y3)],fill=(0,255,0),width=int(IMAGE_HEIGHT*3/4))
    image.save("test.png")


wave()