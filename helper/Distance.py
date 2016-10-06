from enum import Enum
import numpy as np
import scipy.spatial.distance as dist
import cv2


class DistanceType(Enum):
    CHISQUARE = 'ChiSquare'
    L1 = 'L1'
    L2 = 'L2'


def distance(query_hist, other_hists, type):
    if type == DistanceType.CHISQUARE:
        return chi2_distance(query_hist, other_hists)
    if type == DistanceType.L1:
        return l1_distance(query_hist, other_hists)


def chi2_distance(query_hist, other_hists, eps=1e-10):
    d = [(0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                        for (a, b) in zip(query_hist, other_hist)])) for other_hist in other_hists]
    # # compute the chi-squared distance
    # d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
    #                   for (a, b) in zip(query_hist, other_hists)])

    # return the chi-squared distance
    return d


def orb_distance(kp_des, other_kp_dess):
    index_params = dict(algorithm=6, table_number=12, key_size=20, multi_probe_level=2)
    search_params = dict(checks=50)  # or pass empty dictionary
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    kp1, des1 = kp_des
    dis = []
    for other_kp_des in other_kp_dess:
        kp2, des2 = other_kp_des
        matches = flann.knnMatch(des1, des2, k=2)
        tmp_dis = 0
        for match in matches:
            tmp_dis += match[0].distance
        count = len(matches)
        if count > 5:
            dis.append(tmp_dis / count)
        else:
            dis.append(1)
    return dis




def l1_distance(query_hist, other_hists):
    d = [dist.cityblock(query_hist, other_hist) for other_hist in other_hists]
    # d = np.sum([abs(a - b) for (a, b) in zip(query_hist, other_hists)])
    return d
