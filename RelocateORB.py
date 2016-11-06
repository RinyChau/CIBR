from pymongo import MongoClient
import time

# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR

collection = db.ImageFeature
newCollection = db.ORBFeature

imgList = collection.find()
count = 0
start_time = time.time()

for imgItem in imgList:
    newItem = {'_id': imgItem["_id"], 'md5': imgItem['md5'], 'ORB': imgItem['ORB']}
    newCollection.insert_one(newItem)
    del imgItem['ORB']
    collection.replace_one({"_id": imgItem["_id"]}, imgItem)

    count += 1
    if count % 50 == 0:
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))

print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
