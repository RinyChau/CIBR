from sklearn_theano.feature_extraction import GoogLeNetClassifier
import cv2


class CNNClassifier:
    def __init__(self, top_n_classes=2):
        self.clf = GoogLeNetClassifier(top_n=top_n_classes)

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
