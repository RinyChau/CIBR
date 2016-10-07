from helper import PicklePoints
import cv2
from pymongo import MongoClient
import time
import urllib, cStringIO, thread
import numpy as np
from PIL import Image

# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
imgList = list(collection.find())
count = 0
start_time = time.time()
for imgItem in imgList:
    # if "ImageUrl" not in imgItem or imgItem[
    #     "ImageUrl"] != "http://static.pyimagesearch.com.s3-us-west-2.amazonaws.com/vacation-photos/dataset/127503.png":
    #     continue
    image = None
    if image is None and "ImageUrl" in imgItem:
        try:
            file = cStringIO.StringIO(urllib.urlopen(imgItem["ImageUrl"]).read())
            image = np.array(Image.open(file))
            # image = cStringIO.StringIO(urllib.urlopen(imgItem["ImageUrl"]).read())
            # image = Image.open(image)
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except:
            print("unable to fetch image:%s", imgItem["ImageUrl"])

    if image is None and "Path" in imgItem:
        try:
            image = np.array(Image.open("." + imgItem["Path"], 'r'))
        except:
            print("unable to fetch image:%s", imgItem["Path"])

    if image is None and "Path" not in imgItem and "ImageUrl" not in imgItem:
        print("unable to fetch image:%s", imgItem)
        continue
    if image is None:
        continue

    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # Initiate STAR detector
    orb = cv2.ORB_create()
    # find the keypoints with ORB
    kp = orb.detect(image, None)
    # compute the descriptors with ORB
    kp, des = orb.compute(image, kp)

    orb_feature = PicklePoints.pickle_keypoints(kp, des)
    imgItem["ORB"] = orb_feature
    collection.replace_one({"_id": imgItem["_id"]}, imgItem)
    count += 1
    if count % 100 == 0:
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))
print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
