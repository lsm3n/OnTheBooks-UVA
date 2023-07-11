from ocr_func import *
import os, sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

volume = '1959es'

def ocr_cropped_volume(volume, dir = 'cropped'):
    dirpath = sys.path.append(os.path.abspath("./"))
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.3.1/bin/tesseract'
    cwd = os.getcwd()
    cropped = f"{cwd}/images/{volume}/{dir}/"
    print(cropped)
    content = os.listdir(dirpath)
    content = [x for x in os.listdir(cropped) if '_crop.jpg' in x]
    content.sort()
    if(len(content) > 0):
        dir = f"{cwd}/images/{volume}/text/"
        if not os.path.exists("dir"):
            os.makedirs(dir, exist_ok=True)
        print(f"Starting OCR Batch for Volume {volume}")
        for filename in content:
            file = os.path.join(cropped, filename)
            name = filename.replace('_crop.jpg', '.txt')
            target = os.path.join(dir, name)
            print(filename)
            img = Image.open(file)

            text = pytesseract.image_to_string(img)
            ocrf = open(target, mode='w')
            ocrf.write(text)
            ocrf.close()
        print(f"Finished Volume {volume}")




#ocr_cropped_volume('1893-94')
ocr_cropped_volume(volume)
#ocr_cropped_volume('1872-73')
#ocr_cropped_volume('1872-73')
