import logging
import numpy as np

logger = logging.getLogger(__name__)

def crnn_call(mode,images,charset):

    import os
    logger.debug("进程[%d]正在处理一个批次[%d]张图片的识别",os.getpid(),len(images))
    return "abc"

def chunks(list, n):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(list), n):
        yield list[i:i + n]


def test(mode,small_images,charset):
    import math,multiprocessing
    pool = multiprocessing.Pool(processes=3) # 每次创建一个新的进程池，一个请求就会一个，这样会不会有问题，但是这样倒是干净，

    per_num = math.ceil( len(small_images)/3 )
    logger.debug("图片一共[%d]张，划分成[%d]组，每组[%d]张图片",len(small_images),3,per_num)

    # 按照进程池内进程数量的等份图片
    split_images = chunks(small_images,per_num)

    result = []

    i=0
    for images in split_images:
        i+=1
        logger.debug("启动[%d]个进程来处理一组图片：%r",i,np.array(images).shape)
        result.append(
            pool.apply_async(
                crnn_call,
                args=(mode,images,charset,)
            )
        )

    pool.close()
    pool.join()

    logger.debug("所有图片处理识别结束了")

    ocr_result = []
    for _r in result:
        ocr_result+=_r.get()

    return ocr_result


a1 = np.zeros((100,100))
a2 = np.zeros((100,100))
a3 = np.zeros((100,100))
a = [a1,a2,a3]

mode = "string"

charset = {'a','aaaaaa'}

print(test(mode,a,charset))
