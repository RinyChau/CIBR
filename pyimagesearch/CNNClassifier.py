import sys

sys.path.append("app/dist/sklearn_theano-0.0.1-py2.7.egg")
from sklearn_theano.feature_extraction import GoogLeNetClassifier


class CNNClassifier:
    def __init__(self, top_n_classes=2):
        self.clf = GoogLeNetClassifier(top_n=top_n_classes)

    def predict(self, X):
        return self.clf.predict(X)

    def predict_proba(self, X):
        return self.clf.predict_proba(X)
