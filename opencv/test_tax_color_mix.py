from PIL import Image, ImageDraw,  ImageFont
image = Image.new('RGBA', (400,150), color=(128,0,128)) #color=(0,255,0,255)) # 背景是绿色


text_image = Image.new('RGBA', (250,50),color=(255,255,255,0)) 
font = ImageFont.truetype("action.ttf", 50)
draw = ImageDraw.Draw(text_image) 
draw.text((0, 0), "ABC123G8", fill=(0,0,255),font=font) # 字体是蓝色

image.paste(text_image, (50,50), text_image) # 应该是蓝色，而不是青色

image.save("test.png")