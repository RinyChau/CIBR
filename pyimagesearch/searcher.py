# import the necessary packages
import numpy as np
from dao.imagedb import ImageDB
from colordescriptor import Feature
from pyimagesearch.ImageItem import ImageItem
from helper import Distance, PHash
from pyimagesearch.colordescriptor import ColorDescriptor
from helper import PicklePoints
from helper.Distance import DistanceType
import cv2
cv2.ocl.setUseOpenCL(False)
from helper import Labels


class Searcher:
    def __init__(self, dis_type=DistanceType.CHISQUARE, feature_type=Feature.HSV, top_n_classes=2):
        self.dis_type = dis_type
        self.feature_type = feature_type
        self.cd = ColorDescriptor(feature=feature_type)
        # initialize CNNClassifier
        self.top_n_classes = top_n_classes

        self.imgItem = ImageItem(top_n_classes=top_n_classes)

    def search(self, image_path):
        img_item = self.imgItem.ParseImageItem(image_path)
        return self.search_by_features(img_item)

    def search_by_features(self, img_item):
        if "pre_labels" not in img_item:
            img_item["pre_labels"] = Labels.convert_to_label_array(img_item["labels"])
        if "labels" in img_item:
            print img_item["labels"]
        if "kp" not in img_item or "des" not in img_item:
            img_item["kp"], img_item["des"] = PicklePoints.unpickle_keypoints(img_item["ORB"])
        image_list = ImageDB.getListByLabels(labels=img_item["pre_labels"])
        image_list = [x for x in image_list if "PHash" in x and self.feature_type in x and "ORB" in x]

        color_dis = Distance.distance(img_item[self.feature_type],
                                      [img[self.feature_type] for img in image_list], self.dis_type)
        phash_dis = Distance.l1_distance(img_item["PHash"], [img["PHash"] for img in image_list])

        rlabels_dis = Distance.RLabel_distance(img_item["tags"], [img["tags"] for img in image_list])
        color_dis_max = max(color_dis) + 1e-10

        dis_list = ((np.array(color_dis) / color_dis_max) ** 2) + (((np.array(phash_dis) * 1.0) / 64) ** 2) \
                   + (rlabels_dis ** 2)
        max_indices = dis_list.argsort(dis_list)[:200]
        image_list = np.array(image_list)[max_indices]
        dis_list = dis_list[max_indices]

        orb_dis = Distance.orb_distance((img_item["kp"], img_item["des"]),
                                        [PicklePoints.unpickle_keypoints(x["ORB"]) for x in image_list])
        orb_dis_max = max(orb_dis) + 1e-10
        dis_list += ((np.array(orb_dis) * 1.0 / orb_dis_max) ** 2)

        list_len = len(image_list)
        for i in range(list_len):
            image = image_list[i]
            image["distance"] = dis_list[i].item()
            if "ImageUrl" in image:
                image["path"] = image["ImageUrl"]
            else:
                image["path"] = image["Path"]
        image_list.sort(key=lambda x: x["distance"])
        return {"labels":img_item["labels"],"data":image_list}

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

