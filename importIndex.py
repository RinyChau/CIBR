from pyimagesearch.colordescriptor import ColorDescriptor
import argparse
import glob
import cv2
import csv
import datetime
import hashlib
import numpy as np
from pymongo import MongoClient
from bson.objectid import ObjectId


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required = True,
        help = "Path to the directory that contains the images to be indexed")
ap.add_argument("-u", "--url", required = False,
        help = "Path to the url directory that contains the images to be indexed")
args = vars(ap.parse_args())

# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR



# initialize the color descriptor
cd = ColorDescriptor((8, 12, 3))

# use glob to grab the image paths and loop over them
for imagePath in glob.glob(args["dataset"] + "/*.png"):
    # extract the image ID (i.e. the unique filename) from the image
    # path and load the image itself
    imgObj = {}
    imgObj["ImageName"] = imagePath[imagePath.rfind("/") + 1:]
    image = cv2.imread(imagePath)
    imgObj['HSVFeature'] = [x.item() for x in cd.describe(image)]
    #imgObj["HSVFeature"]  = [type(x) for x in  cd.describe(image)[:1]]
    imgObj["md5"] = md5(imagePath)
    imgObj["CreateTime"] = datetime.datetime.utcnow()
    imgObj["UpdateTime"] = datetime.datetime.utcnow()
    if 'url' in args:
        imgObj["ImageUrl"] = args['url'].strip('/')+'/'+ imgObj["ImageName"]
    imgObj["Path"] = "/"+imagePath
    #print(imgObj)
    db.ImageFeature.insert_one(imgObj)
