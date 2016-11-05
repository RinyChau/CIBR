from pymongo import MongoClient
import time
from pyimagesearch.RCNNClassifer import RCNNClassifier

# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
imgList = collection.find()
count = 0
start_time = time.time()

rclf = RCNNClassifier()


for imgItem in imgList:
    if "rlabels" in imgItem:
        del imgItem["rlabels"]
        collection.replace_one({"_id": imgItem["_id"]}, imgItem)
        count += 1
        continue
    else:
        continue

    image_path = "." + imgItem["Path"]
    imgItem["rlabels"] = rclf.detect(image_path)

    collection.replace_one({"_id": imgItem["_id"]}, imgItem)
    count += 1
    if count % 50 == 0:
        print(imgItem["rlabels"])
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))

print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
