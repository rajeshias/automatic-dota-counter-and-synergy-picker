from PIL import Image
import os.path, sys

path = "C:\\Users\\rajes\\OneDrive\\Desktop\\Dota_picker\\heroes copy"
dirs = os.listdir(path)

def crop():
    for item in dirs:
        fullpath = os.path.join(path,item)         #corrected
        if os.path.isfile(fullpath):
            im = Image.open(fullpath)
            f, e = os.path.splitext(fullpath)
            imCrop = im.crop((5, 2, 87, 60)) #corrected
            imCrop.save(f + '.png', "png", quality=100)

crop()