# import the necessary packages
import numpy as np
import cv2
from enum import Enum


class Feature(Enum):
    HSV = 'HSVFeature'
    LUV = 'LUVFeature'



class ColorDescriptor:
    def __init__(self, bins=[8, 12, 3], luv_repre_num=10, feature=Feature.HSV):
        # store the number of bins for the 3D histogram
        self.bins = bins
        self.luv_repre_num = luv_repre_num
        self.luv_repre_colors = []
        self.feature = feature
        l_interval = int(100 / self.luv_repre_num)
        u_interval = int(200 / self.luv_repre_num)
        (l, u, v) = (int(l_interval / 2), int(u_interval / 2), int(u_interval / 2))
        for i in range(0, self.luv_repre_num):
            self.luv_repre_colors.append(np.array((l + l_interval * i, u + u_interval * i, u + u_interval * i)))

    def describe(self, image):
        if self.feature == Feature.HSV:
            return self.describe_hsv(image)
        elif self.feature == Feature.LUV:
            return self.describe_luv(image)

    def describe_hsv(self, image):
        # convert the image to the HSV color space and initialize
        # the features used to quantify the image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []

        # grab the dimensions and compute the center of the image
        (h, w) = image.shape[:2]
        (cX, cY) = (int(w * 0.5), int(h * 0.5))

        # divide the image into four rectangles/segments (top-left,
        # top-right, bottom-right, bottom-left)
        segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h),
                    (0, cX, cY, h)]

        # construct an elliptical mask representing the center of the
        # image
        (axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
        ellipMask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)

        # loop over the segments
        for (startX, endX, startY, endY) in segments:
            # construct a mask for each corner of the image, subtracting
            # the elliptical center from it
            cornerMask = np.zeros(image.shape[:2], dtype="uint8")
            cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
            cornerMask = cv2.subtract(cornerMask, ellipMask)

            # extract a color histogram from the image, then update the
            # feature vector
            hist = self.histogram(image, cornerMask)
            features.extend(hist)

        # extract a color histogram from the elliptical region and
        # update the feature vector
        hist = self.histogram(image, ellipMask)
        features.extend(hist)

        # return the feature vector
        features = [x.item() for x in features]
        return features

    def describe_luv(self, image):

        print("***\n")
        print(image)
        print("***\n")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2LUV)
        segments = self.getSegements(image)
        center = self.getCenterMask(image)

        features = []
        # loop over the segments
        for (startX, endX, startY, endY) in segments:
            # construct a mask for each corner of the image, subtracting
            # the elliptical center from it
            corner_mask = np.zeros(image.shape[:2], dtype="uint8")
            cv2.rectangle(corner_mask, (startX, startY), (endX, endY), 1, -1)
            corner_mask = cv2.subtract(corner_mask, center["mask"])
            # extract a color histogram from the image, then update the
            # feature vector
            hist = self.luv_pw_historgram(image, {"region": (startX, startY, endX, endY), "mask": corner_mask})
            features.extend(hist)

        # extract a color histogram from the elliptical region and
        # update the feature vector
        # (h, w) = image.shape[:2]
        hist = self.luv_pw_historgram(image, center)
        features.extend(hist)


    def luv_pw_historgram(self, image, maskObj, eps=1e-10):
        (startX, startY, endX, endY) = maskObj["region"]
        mask = maskObj["mask"]
        image = image[startY:endY, startX:endX, :]
        mask = mask[startY:endY, startX:endX]
        count = mask.sum()
        dis_repre_array = []
        inverse_dis_sum = np.zeros(image.shape[:2])
        for repre_luv in self.luv_repre_colors:
            dis_repre = (image - repre_luv)
            dis_repre = (1 / (np.sqrt((dis_repre ** 2).sum(axis=2)) + eps))
            dis_repre_array.append(dis_repre)
            inverse_dis_sum += dis_repre

        hist = []
        for i in range(0, len(dis_repre_array)):
            hist.append(((dis_repre_array[i] / inverse_dis_sum) * mask).sum() / count)
        return hist

    def getSegements(self, image):
        # grab the dimensions and compute the center of the image
        (h, w) = image.shape[:2]
        (cX, cY) = (int(w * 0.5), int(h * 0.5))

        # divide the image into four rectangles/segments (top-left,
        # top-right, bottom-right, bottom-left)
        segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h),
                    (0, cX, cY, h)]
        return segments

    def getEllipticalMask(self, image):
        # construct an elliptical mask representing the center of the
        # image
        (h, w) = image.shape[:2]
        (cX, cY) = (int(w * 0.5), int(h * 0.5))
        (axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
        ellipMask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)
        return ellipMask

    def getCenterMask(self, image):
        (h, w) = image.shape[:2]
        (startX, startY, endX, endY) = (int(w * 0.25), int(h * 0.25), int(w * 0.75), int(h * 0.75))
        corner_mask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.rectangle(corner_mask, (startX, startY), (endX, endY), 1, -1)
        return {"region": (startX, startY, endX, endY), "mask": corner_mask}

    def histogram(self, image, mask):
        # extract a 3D color histogram from the masked region of the
        # image, using the supplied number of bins per channel; then
        # normalize the histogram
        hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins,
                            [0, 180, 0, 256, 0, 256])
        cv2.normalize(hist, hist)
        hist = hist.flatten()
        # return the histogram
        return hist
