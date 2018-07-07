import cv2
data = cv2.imread("problem.gif",cv2.IMREAD_LOAD_GDAL)
print(data)

data = cv2.imread("testgif.gif")
print(data)

data = cv2.imread("test.jpg")
print("opencv:shape:")
print(data.shape)


from skimage import io
img=io.imread('problem.jpg')
print(type(img))
print(img.shape)

from PIL import Image
im = Image.open("problem.jpg")
print(type(im))


