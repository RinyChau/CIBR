# import the necessary packages
import numpy as np
from dao.imagedb import ImageDB
from enum import Enum
from colordescriptor import Feature


class DistanceType(Enum):
    CHISQUARE = 'ChiSquare'
    L1 = 'L1'
    L2 = 'L2'

class Searcher:
    def __init__(self, dis_type=DistanceType.CHISQUARE, feature_type=Feature.HSV):
        self.dis_type = dis_type
        self.feature_type = feature_type

    def search(self, queryFeatures, limit=10, forceRefresh=False):
        results = {}
        image_list = ImageDB.getList(force_refresh=forceRefresh)
        for image in image_list:
            if self.feature_type in image:
                features = image[self.feature_type]
                distance = self.distance(features, queryFeatures)
                if "ImageUrl" in image:
                    results[image["ImageUrl"]] = distance
                else:
                    results[image["Path"]] = distance
        results = sorted([v, k] for (k,v) in results.items())

        return results[:limit]

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

        #     if self.feature_type in image:
        #         results.append(image)
        # features = image[self.feature_type]
        # distance = self.distance(features, queryFeatures)
        # if "ImageUrl" in image:
        #     results[image["ImageUrl"]] = distance
        # else:
        #     results[image["Path"]] = distance
        # results = sorted([v, k] for (k,v) in results.items())





    def distance(self, histA, histB):
        if self.dis_type == DistanceType.CHISQUARE:
            return Searcher.chi2_distance(histA, histB)
        if self.dis_type == DistanceType.L1:
            return Searcher.l1_distance(histA, histB)

    @staticmethod
    def chi2_distance(histA, histB, eps=1e-10):
        # compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                          for (a, b) in zip(histA, histB)])

        # return the chi-squared distance
        return d

    @staticmethod
    def l1_distance(histA, histB):
        d = np.sum([abs(a - b) for (a, b) in zip(histA, histB)])
        return d
