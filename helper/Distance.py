from enum import Enum
import numpy as np


class DistanceType(Enum):
    CHISQUARE = 'ChiSquare'
    L1 = 'L1'
    L2 = 'L2'


def distance(self, query_hist, other_hists, type):
    if type == DistanceType.CHISQUARE:
        return chi2_distance(query_hist, other_hists)
    if type == DistanceType.L1:
        return l1_distance(query_hist, other_hists)


def chi2_distance(query_hist, other_hists, eps=1e-10):
    # compute the chi-squared distance
    d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
                      for (a, b) in zip(histA, histB)])

    # return the chi-squared distance
    return d


def l1_distance(histA, histB):
    d = np.sum([abs(a - b) for (a, b) in zip(histA, histB)])
    return d
