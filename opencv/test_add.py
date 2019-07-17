import cv2
# Load two images
img1 = cv2.imread('messi.jpg')
img2 = cv2.imread('logo.jpg')
print("img1:",img1.shape)
print("img2:",img2.shape)
# I want to put logo on top-left corner, So I create a ROI
rows,cols,channels = img2.shape
roi = img1[0:rows, 0:cols ]

# Now create a mask of logo and create its inverse mask also
img2gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
mask_inv = cv2.bitwise_not(mask)
cv2.imshow('mask掩码',mask_inv)
cv2.waitKey(0)


# Now black-out the area of logo in ROI
img1_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
cv2.imshow('messi背景',img1_bg)
cv2.waitKey(0)

# Take only region of logo from logo image.
img2_fg = cv2.bitwise_and(img2,img2,mask = mask)
cv2.imshow('logo前景',img2_fg)
cv2.waitKey(0)

# Put logo in ROI and modify the main image
print("img1_bg:",img1_bg.shape)
print("img2_fg:",img2_fg.shape)
dst = cv2.add(img1_bg,img2_fg)
print("dst:",dst.shape)
img1[0:rows, 0:cols ] = dst
print("img1:",img1.shape)
cv2.imshow('merge合并图像',img1)
cv2.waitKey(0)

cv2.destroyAllWindows()