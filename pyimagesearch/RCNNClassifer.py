import sys, os


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


py_rcnn_root = "/home/liulu/lin/py-faster-rcnn-imagenet"
caffe_path = os.path.join(py_rcnn_root, "caffe-fast-rcnn", "python")
lib_path = os.path.join(py_rcnn_root, 'lib')
add_path(caffe_path)
add_path(lib_path)

from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
import numpy as np
import scipy.io as sio
import caffe, os, sys, cv2


class RCNNClassifier:
    def __init__(self, CONF_THRESH=0.8, NMS_THRESH=0.3):
        self._conf_thres = CONF_THRESH
        self._nms_thresh = NMS_THRESH
        CLASSES = ('__background__',)
        model_root = '/home/liulu/lin/app/model'
        synsets = sio.loadmat(os.path.join(model_root, 'VGG16', 'meta_det.mat'))
        for i in xrange(200):
            CLASSES = CLASSES + (synsets['synsets'][0][i][2][0],)
        self._classes = CLASSES

        cfg.TEST.HAS_RPN = True
        prototxt = os.path.join(os.path.join(model_root, 'VGG16', 'test.prototxt'))
        caffemodel = os.path.join(os.path.join(model_root, 'VGG16', 'vgg16_faster_rcnn_iter_80000.caffemodel'))
        caffe.set_mode_gpu()
        caffe.set_device(0)
        cfg.GPU_ID = 0

        self.net = caffe.Net(prototxt, caffemodel, caffe.TEST)

        print '\n\nLoaded network'
        im = 128 * np.ones((300, 500, 3), dtype=np.uint8)

        # Warm up on a dummy image
        for i in xrange(2):
            _, _ = im_detect(self.net, im)

    def detect(self, imagePath):

        im = cv2.imread(imagePath)
        scores, boxes = im_detect(self.net, im)

        result = {"obj_list": [], "tags": []}
        for cls_ind, class_name in enumerate(self._classes[1:]):
            cls_ind += 1  # because we skipped background
            cls_boxes = boxes[:, 4 * cls_ind:4 * (cls_ind + 1)]
            cls_scores = scores[:, cls_ind]
            dets = np.hstack((cls_boxes,
                              cls_scores[:, np.newaxis])).astype(np.float32)
            keep = nms(dets, self._nms_thresh)
            dets = dets[keep, :]
            inds = np.where(dets[:, -1] >= self._conf_thres)[0]
            for i in inds:
                score = dets[i, -1]
                if class_name in result:
                    result[class_name] += 1
                else:
                    result[class_name]
                result["obj_list"].append({"class_name": class_name, "prob": score, "bbox": dets[i, :4]})
                if class_name not in result["tags"]:
                    result["tags"][class_name] = 1
        return result
