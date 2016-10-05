from pymongo import MongoClient
import time
from PIL import Image
import urllib, cStringIO
import imagehash



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
            image = cStringIO.StringIO(urllib.urlopen(imgItem["ImageUrl"]).read())
            image = Image.open(image)
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        except:
            print("unable to fetch image:%s", imgItem["ImageUrl"])

    if image is None and "Path" in imgItem:
        try:
            image = Image.open("." + imgItem["Path"])
        except:
            print("unable to fetch image:%s", imgItem["Path"])

    if image is None and "Path" not in imgItem and "ImageUrl" not in imgItem:
        print("unable to fetch image:%s", imgItem)
        continue
    if image is None:
        continue

    phash = imagehash.phash(image)
    imgItem["PHash"] = [1 if x.item() else 0 for x in phash.hash.flatten()]
    collection.replace_one({"_id": imgItem["_id"]}, imgItem)
    count += 1
    if count % 100 == 0:
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))
print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
