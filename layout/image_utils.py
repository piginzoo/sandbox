from bbox import BBox
from points_tool import *
from PIL import Image, ImageDraw, ImageFont

def get_rotated_text_image(bbox, bg_color, font_size):
    pos = bbox.pos
    width = pos[:, 0].max() - pos[:, 0].min()
    height = pos[:, 1].max() - pos[:, 1].min()
    # 给丫画出来
    words_image = Image.new('RGBA', (width, height))

    text = bbox.txt
    # 计算这个框的旋转角度
    arc = caculate_rect_inclination(pos)
    # 给丫转平
    horizental_pos = rotate_rect_by_center(pos, -arc)
    # 算丫呢宽高
    horizental_width = horizental_pos[:, 0].max() - horizental_pos[:, 0].min()
    horizental_height = horizental_pos[:, 1].max() - horizental_pos[:, 1].min()
    x = 0
    y = int((height - horizental_height)/2)

    # 先填充背景
    words_image.paste(bg_color, [x,y,x+horizental_width,y+horizental_height])

    draw = ImageDraw.Draw(words_image,"RGBA")
    # 注意下，下标是从0,0开始的，是自己的坐标系
    font = ImageFont.truetype("data/simsun.ttc", font_size)
    draw.text((x+5,y+5), text, fill=(0, 0, 0), font=font)
    degree = math.degrees(arc)
    words_image = words_image.rotate(-degree)
    return words_image


def rotate(image, angle, center=None, scale=1.0):  # 1
    (h, w) = image.shape[:2]  # 2
    if center is None:  # 3
        center = (w // 2, h // 2)  # 4

    M = cv2.getRotationMatrix2D(center, angle, scale)  # 5

    rotated = cv2.warpAffine(image, M, (w, h))  # 6
    return rotated


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG,handlers=[logging.StreamHandler()])
    image = np.full([400, 400, 3], 0, np.uint8)

    _pos = [[ 69,  28],
       [155,  78],
       [130, 121],
       [ 44,  71]]
    pos = np.array(_pos)

    # cv2.polylines(image,[pos],True,(255,255,0),thickness=5)

    x = pos[:,0].min()
    y = pos[:, 1].min()

    _bbox = BBox(pos,"我爱鳖精~")
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    word_images = get_rotated_text_image(_bbox,(255,255,255))
    image.paste(word_images,(x,y))
    image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    cv2.imwrite("debug/image_test.jpg",image)


