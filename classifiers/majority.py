from classifiers.classifier import Classifier
import collections

class Majority(Classifier):

    def train(self, X, y, meta=None):
        self.label = collections.Counter(y).most_common(1)[0][0]

    def predict(self, X):
        return [self.label]*len(X)

    def predict_proba(self, X):
        raise Exception("Unsupported operation")
