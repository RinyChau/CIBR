from pyimagesearch.colordescriptor import ColorDescriptor
import datetime
import hashlib
import numpy as np
from PIL import Image
from pyimagesearch.colordescriptor import Feature
import imagehash
from helper import PicklePoints, Labels
from pyimagesearch.CNNClassifier import CNNClassifier
import cv2

cv2.ocl.setUseOpenCL(False)


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class ImageItem:
    def __init__(self, hsv_bins=(8, 12, 3), top_n_classes=5):
        self.hsv_cd = ColorDescriptor(hsv_bins, feature=Feature.HSV)
        self.luv_cd = ColorDescriptor(feature=Feature.LUV)
        self.clf = CNNClassifier(top_n_classes=top_n_classes)
        self.orb = cv2.ORB_create()

    def ParseImageItem(self, imagePath):
        imgItem = {"md5": md5(imagePath), "ImageName": imagePath[imagePath.rfind("/") + 1:],
                   "CreateTime": datetime.datetime.utcnow(), "UpdateTime": datetime.datetime.utcnow()}

        # features
        image_src = Image.open(imagePath)
        image = np.array(image_src)
        imgItem[Feature.HSV] = [x for x in self.hsv_cd.describe(image)]
        imgItem[Feature.LUV] = self.luv_cd.describe(image)
        phash = imagehash.phash(image_src)
        imgItem["PHash"] = [x.item() for x in phash.hash.flatten()]

        # CNN labels
        labels, probs = self.clf.predict_label_proba(image)
        imgItem["labels"] = Labels.convert_to_dic(labels, probs)

        # ORB
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        kp, des = self.orb.detectAndCompute(gray_image, None)
        imgItem["ORB"] = PicklePoints.pickle_keypoints(kp, des)

        return imgItem
