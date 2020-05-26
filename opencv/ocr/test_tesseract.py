import cv2, pytesseract
image = cv2.imread("data/test3.png",0)
# image = cv2.resize(image,None,fx=5,fy=5,interpolation=cv2.INTER_AREA)
ret, binary = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)
# cv2.imshow("Image", binary)
# cv2.waitKey(0)
text = pytesseract.image_to_string(binary, lang='chi_sim')

print(text)