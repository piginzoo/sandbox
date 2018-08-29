import pytesseract
from PIL import Image

image = Image.open('report.jpg')
code = pytesseract.image_to_string(image)
print(code)
