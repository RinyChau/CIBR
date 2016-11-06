from pymongo import MongoClient
import time

# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
imgList = collection.find()
count = 0
start_time = time.time()
for imgItem in imgList:
    tag_set = set()
    for tag in imgItem["rlabels"]["tags"]:
        tag_set.add(tag.keys()[0])
    imgItem["rlabels"]["tags"] = list(tag_set)
    collection.replace_one({"_id": imgItem["_id"]}, imgItem)

    count += 1
    if count % 50 == 0:
        print(imgItem["labels"])
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))
print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
