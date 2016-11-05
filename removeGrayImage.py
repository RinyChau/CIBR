import os,cv2
import numpy as np
from PIL import Image
import Image as Image2
from scipy.misc import imread, imsave, imresize

all_imgs = []
for path, subdirs, files in os.walk("./static/image"):
    for name in files:
        all_imgs.append(os.path.join(path, name))



for path in all_imgs:
    try:
        im = Image.open(path)
        im.verify()
    except:
        print("cannot get image" + path)
        continue
    image = imread(path)
    if(len(image.shape)<3):
        print path
        print "gray image"
        os.remove(path)
