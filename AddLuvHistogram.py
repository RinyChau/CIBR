from pyimagesearch.colordescriptor import ColorDescriptor
import cv2
import hashlib
from pymongo import MongoClient
from skimage import io


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

cd = ColorDescriptor((8, 12, 3), 10)

for imgItem in imgList:
    if "ImageUrl" in imgItem:
        image = io.imread(imgItem["ImageUrl"])
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image = cv2.imread("." + image["Path"])
    luv_feature = cd.describe_luv(image)
    imgItem["LUVFeature"] =  luv_feature
    collection.replace_one({"_id": imgItem["_id"]}, imgItem)
