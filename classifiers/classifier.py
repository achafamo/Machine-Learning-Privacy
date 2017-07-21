class Classifier(object):

    def train(self, X, y, meta=None):
        """Trains the classifier on training data X with labels y.  meta, if available,
        contains metadata about the dataset (such as number of features, feature types, etc.
        """
        raise Exception("Abstract class.  Subclass must override.")

    def predict(self, X):
        """Returns a list of label predictions for instances X"""
        raise Exception("Abstract class.  Subclass must override.")

    def predict_proba(self, X):
        """Returns a probability distributions over labels for instances X"""
        raise Exception("Abstract class.  Subclass must override.")

    def accuracy(self, X, y):
        """Returns accuracy of classifier when predicts labels for input X.  Ground
        truth is y.
        """
        assert len(X) == len(y)
        assert len(y) > 0
        return float(sum(guess == truth for (guess, truth) in zip(self.predict(X), y))) / len(y)