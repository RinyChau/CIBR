from pyimagesearch.colordescriptor import ColorDescriptor
import argparse
import glob
import cv2
cv2.ocl.setUseOpenCL(False)
import datetime
import hashlib
import numpy as np
from pymongo import MongoClient
from PIL import Image
from pyimagesearch.colordescriptor import Feature
import imagehash
from helper import PicklePoints, Labels
import urllib, cStringIO
import time
import os
from pyimagesearch.CNNClassifier import CNNClassifier
from pyimagesearch.ImageItem import ImageItem


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
                help="Path to the directory that contains the images to be indexed")
ap.add_argument("-u", "--url", required=False,
                help="Path to the url directory that contains the images to be indexed")
args = vars(ap.parse_args())

# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
# initialize the color descriptor
hsv_cd = ColorDescriptor((8, 12, 3), feature=Feature.HSV)
luv_cd = ColorDescriptor(feature=Feature.LUV)
top_n_classes = 5
clf = CNNClassifier(top_n_classes=top_n_classes)
start_time = time.time()
count = 0

imageItem = ImageItem()

all_imgs = []
for path, subdirs, files in os.walk(args["dataset"]):
    for name in files:
        all_imgs.append(os.path.join(path, name))

# use glob to grab the image paths and loop over them
for imagePath in all_imgs:
    # extract the image ID (i.e. the unique filename) from the image
    # print(imagePath)
    try:
        im = Image.open(imagePath)
        im.verify()
    except:
        print("cannot get image" + imagePath)
        continue

    file_md5 = md5(imagePath)
    same_imgs = list(collection.find({"md5": file_md5}))
    if len(same_imgs) > 0:
        print("same image" + imagePath)
        continue

    imgObj = imageItem.ParseImageItem(imagePath)
    imgObj["Path"] = "/" + imagePath
    # print(imgObj)
    collection.insert_one(imgObj)

    count += 1
    if count % 100 == 0:
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))

print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
