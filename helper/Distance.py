from enum import Enum
import numpy as np
import scipy.spatial.distance as dist
import cv2
import math
import time


class DistanceType:
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


MAX_DISTANCE = 128


def orb_distance(kp_des, other_kp_dess):
    index_params = dict(algorithm=6, table_number=12, key_size=20, multi_probe_level=2)
    search_params = dict(checks=50)  # or pass empty dictionary
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    kp1, des1 = kp_des
    dis = []
    for other_kp_des in other_kp_dess:
        kp2, des2 = other_kp_des
        if des2.size == 0:
            dis.append(MAX_DISTANCE)
            continue
        matches = flann.knnMatch(des1, des2, k=2)
        matches = [match[0].distance if len(match) > 0 else MAX_DISTANCE for match in matches]
        count = len(matches)
        tmp_dis = float(sum(matches)) / count
        # for match in matches:
        #     if len(match) > 0:
        #         tmp_dis += match[0].distance
        #     else:
        #         tmp_dis = MAX_DISTANCE
        # count = len(matches)
        if count > 5:
            dis.append(tmp_dis * 1.0 / count)
        else:
            dis.append(MAX_DISTANCE)
            # print(max([match[1].distance if len(match) > 1 else 0 for match in matches]))
    return dis


def l1_distance(query_hist, other_hists):
    d = [dist.cityblock(query_hist, other_hist) for other_hist in other_hists]
    # d = np.sum([abs(a - b) for (a, b) in zip(query_hist, other_hists)])
    return d


def RLabel_distance(rlabels, other_rlabels):
    start_time = time.time()
    d = []
    for other_rlabel in other_rlabels:
        label_set = set(rlabels.keys()).union(other_rlabel.keys())
        sim = 0
        common_obj = 0
        total_obj = 0
        for class_name in label_set:
            if class_name == "obj_list" or class_name == "tags":
                continue
            num_a = 0 if class_name in rlabels else rlabels[class_name]
            num_b = 0 if class_name in other_rlabel else other_rlabel[class_name]
            common_obj += 2 * min(num_a, num_b)
            total_obj += num_a + num_b
            sim += math.log(min(num_a, num_b)) * (1 - abs(num_a - num_b) / (num_a + num_b))
        sim *= (common_obj * 1.0 / total_obj)
        d.append(sim)
    dis_max = max(d) + 1e-10
    d = 1 - (np.array(d) / dis_max)
    print("count {}".format(len(d)))
    print(" --- %s seconds ---" % (time.time() - start_time))
    return d
