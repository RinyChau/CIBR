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


class CNNClassifier:
    def __init__(self, CONF_THRESH=0.8, NMS_THRESH=0.3):
        self._conf_thres = CONF_THRESH
        self._nms_thresh = NMS_THRESH
        CLASSES = ('__background__',)
        model_root = '/home/liulu/lin/app/model'
        synsets = sio.loadmat(os.path.join(model_root, 'VGG16', 'meta_det.mat'))
        for i in xrange(200):
            CLASSES = CLASSES + (synsets['synsets'][0][i][2][0],)
        self._classes = CLASSES
        prototxt = os.path.join(os.path.join(model_root, 'VGG16', 'test.prototxt'))
        caffemodel = os.path.join(os.path.join(model_root, 'VGG16', 'vgg16_faster_rcnn_iter_80000.caffemodel'))
        caffe.set_mode_gpu()
        caffe.set_device(0)
        cfg.GPU_ID = 0
        net = caffe.Net(prototxt, caffemodel, caffe.TEST)

        print '\n\nLoaded network'
        im = 128 * np.ones((300, 500, 3), dtype=np.uint8)

        # Warm up on a dummy image
        for i in xrange(2):
            _, _ = im_detect(net, im)

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

    def predict(self, X):
        res = cv2.resize(X, (231, 231), interpolation=cv2.INTER_LINEAR)
        labels = self.clf.predict(res).ravel()[::-1]
        return labels

    def predict_proba(self, X):
        res = cv2.resize(X, (231, 231), interpolation=cv2.INTER_LINEAR)
        probs = self.clf.predict_proba(res).ravel()[::-1]
        return probs

    def predict_label_proba(self, X):
        res = cv2.resize(X, (231, 231), interpolation=cv2.INTER_LINEAR)
        labels = self.clf.predict(res).ravel()[::-1]
        probs = self.clf.predict_proba(res).ravel()[::-1]
        return labels, probs


def vis_detections(image_name, im, class_name, dets, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        return

    # im = im[:, :, (2, 1, 0)]
    # fig, ax = plt.subplots(figsize=(12, 12))
    # ax.imshow(im, aspect='equal')
    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]
        cv2.rectangle(im, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 3)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(im, '{:s} {:.3f}'.format(class_name, score), (int(bbox[0]), int(bbox[1] - 2)), font, 1, (0, 0, 255),
                    2, cv2.LINE_AA)
        # ax.add_patch(
        #    plt.Rectangle((bbox[0], bbox[1]),
        #                  bbox[2] - bbox[0],
        #                  bbox[3] - bbox[1], fill=False,
        #                  edgecolor='red', linewidth=3.5)
        #    )
        # ax.text(bbox[0], bbox[1] - 2,
        #        '{:s} {:.3f}'.format(class_name, score),
        #        bbox=dict(facecolor='blue', alpha=0.5),
        #        fontsize=14, color='white')

    # ax.set_title(('{} detections with '
    #             'p({} | box) >= {:.1f}').format(class_name, class_name,
    #                                              thresh),
    #              fontsize=14)
    # plt.axis('off')
    # plt.tight_layout()
    # plt.draw()
    # save the image
    # fig = plt.gcf()
    # fig.savefig("output_"+image_name)
    cv2.imwrite("output_" + image_name, im)
