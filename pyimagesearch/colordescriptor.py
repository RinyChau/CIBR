# import the necessary packages
import numpy as np
import cv2


class ColorDescriptor:
    def __init__(self, bins, luv_repre_num=10):
        # store the number of bins for the 3D histogram
        self.bins = bins
        self.luv_repre_num = luv_repre_num
        self.luv_repre_colors = []
        l_interval = int(100 / self.luv_repre_num)
        u_interval = int(200 / self.luv_repre_num)
        (l, u, v) = (int(l_interval / 2), int(u_interval / 2), int(u_interval / 2))
        for i in range(0, self.luv_repre_num):
            self.luv_repre_colors.append(np.array((l + l_interval * i, u + u_interval * i, u + u_interval * i)))

    def describe(self, image):
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
        return features

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

    def describe_luv(self, image):

        image = cv2.cvtColor(image, cv2.COLOR_BGR2LUV)
        segments = self.getSegements(image)
        ellipse_mask = self.getEllipticalMask(image)

        features = []
        # loop over the segments
        for (startX, endX, startY, endY) in segments:
            # construct a mask for each corner of the image, subtracting
            # the elliptical center from it
            corner_mask = np.zeros(image.shape[:2], dtype="uint8")
            cv2.rectangle(corner_mask, (startX, startY), (endX, endY), 255, -1)
            corner_mask = cv2.subtract(corner_mask, ellipse_mask)
            # extract a color histogram from the image, then update the
            # feature vector
            hist = self.luv_pw_historgram(image, corner_mask, (startX, endX, startY, endY))
            features.extend(hist)

        # extract a color histogram from the elliptical region and
        # update the feature vector
        (h, w) = image.shape[:2]
        hist = self.luv_pw_historgram(image, ellipse_mask, (0, w, 0, h))
        features.extend(hist)

    def luv_pw_historgram(self, image, corner_mask, region):
        (start_x, end_x, start_y, end_y) = region
        print(region)
        hist = np.zeros((1, self.luv_repre_num))
        count = 0
        for x in range(start_x, end_x):
            for y in range(start_y, end_y):
                if corner_mask[x][y] > 0:
                    count += 1
                    luv = np.array((image[x][y][0], image[x][y][1], image[x][y][2]))
                    dis_his = []
                    for repre_luv in self.luv_repre_colors:
                        dis_his.append(1 / np.linalg.norm(luv - repre_luv))
                    dis_sum = sum(dis_his)
                    dis_his = np.array(dis_his) / dis_sum
                    hist += dis_his
        hist /= count
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
