import sys
sys.path.append("app/dist/sklearn_theano-0.0.1-py2.7.egg")
import hashlib
from pymongo import MongoClient
import time
import urllib, cStringIO
import numpy as np
from pyimagesearch.CNNClassifier import CNNClassifier
from sklearn_theano.feature_extraction import GoogLeNetClassifier
from PIL import Image


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# initialize mongodb client
client = MongoClient()

# Content-based image retrieval database
db = client.CIBR
collection = db.ImageFeature
imgList = list(collection.find())
count = 0
start_time = time.time()
top_n_classes = 5
clf = CNNClassifier(top_n_classes=top_n_classes)
for imgItem in imgList:
    # if "ImageUrl" not in imgItem or imgItem[
    #     "ImageUrl"] != "http://static.pyimagesearch.com.s3-us-west-2.amazonaws.com/vacation-photos/dataset/127503.png":
    #     continue
    image = None

    if image is None and "Path" in imgItem:
        try:
            file_path = "." + imgItem["Path"]
            image = np.array(Image.open(file_path, 'r'))
        except:
            print("unable to fetch image:%s", imgItem["Path"])

    if image is None and "ImageUrl" in imgItem:
        try:
            file = cStringIO.StringIO(urllib.urlopen(imgItem["ImageUrl"]).read())
            image = np.array(Image.open(file))
        except:
            print("unable to fetch image:%s", imgItem["ImageUrl"])

    if image is None and "Path" not in imgItem and "ImageUrl" not in imgItem:
        print("unable to fetch image:%s", imgItem)
        continue
    if image is None:
        continue

    labels = clf.predict(image).ravel()[::-1]
    probs = clf.predict_proba(image).ravel()[::-1]
    if not all(probs[i] >= probs[i + 1] for i in xrange(len(probs) - 1)):
        print("probs is not sorted")
        break
    label = []
    top_n_prob = 0
    length = len(labels)
    for i in range(length):
        tags = labels[i]
        prob = probs[i]
        top_n_prob += 1
        for tag in tags.split(","):
            label.append({"label": tag, "rank": top_n_prob, 'prob': probs[i].item()})

    imgItem["labels"] = label
    collection.replace_one({"_id": imgItem["_id"]}, imgItem)


    # print(result)

    # feature = cd.describe(image)
    # imgItem[feature_type] = feature
    # collection.replace_one({"_id": imgItem["_id"]}, imgItem)
    count += 1
    if count % 50 == 0:
        print(imgItem["labels"])
        print(count)
        print(" --- %s seconds ---" % (time.time() - start_time))
print(count)
print("finish --- %s seconds ---" % (time.time() - start_time))
