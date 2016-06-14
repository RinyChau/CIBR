from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.CIBR
collection = db.ImageFeature
imgList = list(collection.find())
for img in imgList:
    if "ImageUrl" in img:
        del img["Path"]
    else:
        img["Path"] = img["Path"].replace('app', 'static')
        print(img)
    collection.replace_one(img)
