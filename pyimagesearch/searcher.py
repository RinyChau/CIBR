# import the necessary packages
import numpy as np
from dao.imagedb import ImageDB


class Searcher:
    @staticmethod
    def search(queryFeatures, limit=10,forceRefresh=False):
        # initialize our dictionary of results
        results = {}

        for image in ImageDB().getList(force_refresh=forceRefresh):
            features = image["HSVFeature"]
            distance = Searcher.chi2_distance(features, queryFeatures)
            if "ImageUrl" in image:
                results[image["ImageUrl"]] = distance
            else:
                results[image["Path"]] = distance
            
        results = sorted([v, k] for (k,v) in results.items())

        # return our (limited) results
        return results[:limit]

    @staticmethod
    def chi2_distance(histA, histB, eps=1e-10):
        # compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                          for (a, b) in zip(histA, histB)])

        # return the chi-squared distance
        return d
