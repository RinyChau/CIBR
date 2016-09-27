from pymongo import MongoClient

# initialize mongodb client
client = MongoClient("127.0.0.1:5988")

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
imgList = list(collection.find())

for imgItem in imgList:
    if "labels" in imgItem:
        for i in range(len(imgItem["labels"])):
            imgItem["labels"][i]["top_n_prob"] = 6 - imgItem["labels"][i]["top_n_prob"]
        imgItem["labels"].sort(key=lambda x: x["top_n_prob"])
        collection.replace_one({"_id": imgItem["_id"]}, imgItem)
    continue
