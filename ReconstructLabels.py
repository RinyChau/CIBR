from pymongo import MongoClient
import time
import urllib, cStringIO
import numpy as np
from PIL import Image
from helper import Labels

# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
imgList = collection.find()
count = 0
start_time = time.time()
for imgItem in imgList:
    label_set = set()
    label_base = 'label{}'
    prob_base = 'prob{}'
    label_dic = {}
    for label in imgItem["labels"]:
        rank = label["rank"]
        label_key = label_base.format(rank)
        prob_key = prob_base.format(rank)
        if label_key in label_set:
            continue
        label_set.add(label_key)
        label_dic[label_key] = label["label"]
        label_dic[prob_key] = label["prob"]
    imgItem["labels"] = label_dic

    collection.replace_one({"_id": imgItem["_id"]}, imgItem)

    count += 1
    if count % 50 == 0:
        print(imgItem["labels"])
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))
print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
