import base64
import cv2,sys
import json
import requests
import ffmpeg
import numpy

def call(url,image):
    """
    {
         'sid':'2019111314040513',      # 调用session id
         'img':'<BASE64编码>',            # 图片的base64编码
         'imgSign': 'T1',            # 图片标识
         'merchantPrimaryKeyId':'xx',# 主键id
         'merchantPlate' : 'xxxx''   # 车牌号码'
    }


    {
        'sid': '2019111314040513',
        'msg':'success',
        'plate':{
                'plate':'京NHC2222',     # 车牌号
                'position':               # 车牌4点坐标
                    [{"y": 223,"x": 170},
                    {"y": 223,"x": 282},
                    {"y": 256,"x": 282},
                    {"y": 256,"x": 170}],
                'color':'blue',           # 车牌颜色
            },
        'code': 0                       # 错误码
    }
    """
    base64_images = str(base64.b64encode(image), 'utf-8')
    post_data = {
         'sid':'FFPEG123',
         'img':base64_images,
         'imgSign': 'T1',
         'merchantPrimaryKeyId':'000',
         'merchantPlate' : 'XXXXX'
    }
    headers = {'Content-Type': 'application/json'}
    print(f"Call {url} to OCR plate")
    response = requests.post(url,json=post_data,headers=headers)
    r = response.text
    r = json.loads(r)
    # print(r)
    # plate = r['plate']['plate']
    # pos = r['plate']['position']
    # print("plate:",plate)
    # print("position:",pos)
    return r


# ffmpeg -i data/test.mp4 -f image2 -vf fps=fps=1 output/out%d.png
# https://juejin.im/post/5d90a5ac5188250910230c79
def read_frame_by_time(in_file, time):
    """
    指定时间节点读取任意帧
    """
    out, err = (
        ffmpeg.input(in_file, ss=time)
              .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
              .run(capture_stdout=True)
    )
    return out

def get_video_info(in_file):
    """
    获取视频基本信息
    """
    try:
        probe = ffmpeg.probe(in_file)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        if video_stream is None:
            print('No video stream found', file=sys.stderr)
            sys.exit(1)
        return video_stream
    except ffmpeg.Error as err:
        print(str(err.stderr, encoding='utf8'))
        sys.exit(1)


def find_plate(video_path,url):
    video_info = get_video_info(video_path)
    total_duration = int(float(video_info['duration']))
    print(f'总时间：{total_duration} s')

    for i in range(0, total_duration,3): # 每隔3秒
        out = read_frame_by_time(video_path, i)
        image_array = numpy.asarray(bytearray(out), dtype="uint8")
        image1 = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        _, image = cv2.imencode('.jpg', image1)
        result = call(url,image)
        if result['code']!=0: continue

        plate = result['plate']['plate']
        print("找到车牌在：%d 秒 [%s]" % (i,plate))
        pos = result['plate']['position']
        pos = [[p['x'],p['y']] for p in pos]
        print(pos)
        pos = numpy.array(pos,numpy.int32)
        print(pos)
        cv2.polylines(image1,[pos],isClosed=True,color=(0,0,255),thickness=2)
        cv2.imwrite(f"output/{i}_{plate}.jpg",image1)


if __name__=="__main__":
    import sys
    print(sys.argv)
    if len(sys.argv)<=1:
        print("usage: python find_plate.py [host] , host is http://ai.[host].corp/plate")
        exit()

    host = sys.argv[1]

    # image = cv2.imread("output/out2.png")
    # _, image = cv2.imencode('.jpg', image)
    # call(f"http://ai.{host}.corp/plate",image)

    find_plate("data/test.mp4",f"http://ai.{host}.corp/plate")