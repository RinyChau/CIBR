from pyimagesearch.colordescriptor import ColorDescriptor
import cv2
import hashlib
from pymongo import MongoClient
from skimage import io
from pyimagesearch.colordescriptor import Feature
import time


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# initialize mongodb client
client = MongoClient("127.0.0.1:5988")

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
imgList = list(collection.find())
feature_type = Feature.LUV
cd = ColorDescriptor(feature=feature_type)
count = 0
start_time = time.time()
for imgItem in imgList:
    # if "ImageUrl" not in imgItem or imgItem[
    #     "ImageUrl"] != "http://static.pyimagesearch.com.s3-us-west-2.amazonaws.com/vacation-photos/dataset/127503.png":
    #     continue
    image = None
    if image is None and "ImageUrl" in imgItem:
        try:
            image = io.imread(imgItem["ImageUrl"])
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except:
            print("unable to fetch image:%s", imgItem["ImageUrl"])

    if image is None and "Path" in imgItem:
        try:
            image = cv2.imread("." + imgItem["Path"])
        except:
            print("unable to fetch image:%s", imgItem["Path"])



    if image is None and "Path" not in imgItem and "ImageUrl" not in imgItem:
        print("unable to fetch image:%s", imgItem)
        continue
    if image is None:
        continue

    feature = cd.describe(image)
    imgItem[feature_type] = feature
    collection.replace_one({"_id": imgItem["_id"]}, imgItem)
    count += 1
    if count % 100 == 0:
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))
print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
