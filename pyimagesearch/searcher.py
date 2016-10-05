# import the necessary packages
import numpy as np
from dao.imagedb import ImageDB
from enum import Enum
from colordescriptor import Feature
from pyimagesearch.CNNClassifier import CNNClassifier
from helper import Distance, PHash
from pyimagesearch.colordescriptor import ColorDescriptor
from helper import PicklePoints
import cv2
import imagehash
from helper import Distance

class DistanceType(Enum):
    CHISQUARE = 'ChiSquare'
    L1 = 'L1'
    L2 = 'L2'


class Searcher:
    def __init__(self, dis_type=DistanceType.CHISQUARE, feature_type=Feature.HSV, top_n_classes=2):
        self.dis_type = dis_type
        self.feature_type = feature_type
        self.cd = ColorDescriptor(feature=feature_type)
        # initialize CNNClassifier
        self.top_n_classes = top_n_classes
        self.classifier = CNNClassifier(self.top_n_classes)
        self.orb = cv2.ORB_create()

    def search(self, image):
        phash = imagehash.phash(image)
        image = np.array(image)
        pre_labels = self.classifier.predict(image).ravel()[::-1]
        pre_labels = [tags.split(',')[0] for tags in pre_labels]
        probs = self.classifier.predict_proba(image).ravel()[::-1]
        labels = []
        length = len(pre_labels)
        rank = 0
        for i in range(length):
            rank += 1
            labels.append({"label": pre_labels[i], "rank": rank, 'prob': probs[i].item()})

        img_item = {"labels": labels,
                    self.feature_type: self.cd.describe(cv2.cvtColor(image, cv2.COLOR_RGB2BGR)),
                    "PHash": phash.hash.flatten(), "pre_labels": pre_labels}

        kp = self.orb.detect(image, None)
        # compute the descriptors with ORB
        kp, des = self.orb.compute(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), kp)
        orb_feature = PicklePoints.pickle_keypoints(kp, des)
        img_item["ORB"] = orb_feature
        return self.search_by_features(img_item=img_item)
        # return self.search_by_features(img_item)
        # image_list = ImageDB.getListByLabels(labels=labels)
        # color_dis_list = Distance.distance()
        # pass

    def search_by_features(self, img_item):
        if "pre_labels" not in img_item:
            pre_labels = []
            length = img_item["labels"]
            rank = 0
            for i in range(len(length)):
                item = img_item[i]
                if rank != item["rank"]:
                    rank = item["rank"]
                else:
                    continue
                if rank > self.top_n_classes:
                    break
                pre_labels.append(item["label"])
            img_item["pre_labels"] = pre_labels
        image_list = ImageDB.getListByLabels(labels=img_item["pre_labels"])
        image_list = [x for x in image_list if "PHash" in x and self.feature_type in x and "ORB" in x]
        color_dis = Distance.distance(img_item[self.feature_type],
                                      [img[self.feature_type] for img in image_list], self.dis_type)
        # phash_dist = Distance.distance()

        # color_dis_order_index = np.argsort(x)

        list_len = len(image_list)
        for i in range(list_len):
            image = image_list[i]
            image["distance"] = color_dis[i]
            if "ImageUrl" in image:
                image["path"] = image["ImageUrl"]
            else:
                image["path"] = image["Path"]
                if "124001.png" in image["Path"]:
                    print(np.array_equal(image[self.feature_type], img_item[self.feature_type]))
                    if not np.array_equal(image[self.feature_type], img_item[self.feature_type]):
                        print(image[self.feature_type])
                        print(img_item[self.feature_type])
        image_list.sort(key=lambda x: x["distance"])
        return image_list

    # def search(self, queryFeatures, limit=10, forceRefresh=False):
    #     results = {}
    #     image_list = ImageDB.getList(force_refresh=forceRefresh)
    #     for image in image_list:
    #         if self.feature_type in image:
    #             features = image[self.feature_type]
    #             distance = self.distance(features, queryFeatures)
    #             if "ImageUrl" in image:
    #                 results[image["ImageUrl"]] = distance
    #             else:
    #                 results[image["Path"]] = distance
    #     results = sorted([v, k] for (k,v) in results.items())
    #
    #     return results[:limit]

    def search_by_labels(self, queryFeatures, labels, limit=50):
        image_list = ImageDB.getListByLabels(labels=labels)
        results = [x for x in image_list if self.feature_type in x]
        for image in results:
            image["distance"] = self.distance(image[self.feature_type], queryFeatures)
            if "ImageUrl" in image:
                image["path"] = image["ImageUrl"]
            else:
                image["path"] = image["Path"]
        results.sort(key=lambda x: x["distance"])

        # only select the top 1000 pictures
        # results = results[:1000]

        return results[:limit]

# def parse_label(labels):
#     label_list = []
#     # top_n_prob = 0
#     for tags in reversed(labels.ravel()):
#         label_list.append(tags[:tags.index(',')] if ',' in tags else tags)
#         # for tag in tags.split(","):
#         #     label_list.append(tag)
#         #     label.append({"label": tag, "top_n_prob": top_n_prob})
#     return label_list
