from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO


template = Image.open("template.png")


new_image = Image.open("15503_SW_T5_Rd,_Beverly,_WA.jpg")

replacement_area = (113, 190, 980, 730)  


new_image_resized = new_image.resize((replacement_area[2] - replacement_area[0], 
                                      replacement_area[3] - replacement_area[1]))


template.paste(new_image_resized, replacement_area)

def overlay_text_on_image(image, text, y_pos =780, font_size=35):
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", font_size) 
    except IOError:
        font = ImageFont.load_default()  
    text_bbox = draw.textbbox((0, 0), text, font=font)  # Updated line
    text_width = (text_bbox[2] - text_bbox[0])* 1.22  # Calculate width from bbox
    text_height = text_bbox[3] - text_bbox[1]
    print(image.width, text_width)
    position = (image.width // 2 - text_width // 2 , y_pos) 
    text_color = (5, 255, 100)
    draw.text(position, text.upper(), fill=text_color, font=font) 


overlay_text_on_image(template, "15503 SW T5 Rd, Beverly, WA")


template.save("updated_template_with_text.png")

template.show()