from classifiers.classifier import Classifier
import util

# todo: revise because OneRule is just a depth 1 tree using SPLIT_MAX criteria?
class OneRule(Classifier):

    def __init__(self):
        self.feature = None          # the feature used to classify
        self.value_to_label = None   # for each value of self.feature, the class label that will be assigned

    def train(self, X, y, meta=None):
        features = meta.features
        stats = {}   # feature maps to dict of feature value, each value maps to dist over labels
        for feature in features:
            stats[feature] = {}
        for instance,label in zip(X,y):
            for feature, value in instance.items():
                if value not in stats[feature]:
                    stats[feature][value] = util.Counter()
                stats[feature][value][label] += 1

        feature = self._pick_best(stats)
        rule = self._make_rule(feature, stats)
        self.feature = feature
        self.value_to_label = rule

    def _compute_error(self, stats):
        errors = util.Counter()
        for feature in stats:
            # rule(feature) = for each value of feature, pick majority class label from training data
            # error(feature) = # misclassified when we use rule
            error = 0
            for val in stats[feature]:
                most_freq_label = stats[feature][val].argMax()
                error += stats[feature][val].totalCount() - stats[feature][val][most_freq_label]
            errors[feature] = error
        return errors

    def _pick_best(self, stats):
        """Returns the feature with lowest error.
        """
        errors = self._compute_error(stats)
        return errors.argMin()

    def _make_rule(self, feature, stats):
        """Rule is a map from feature value to majority label, which
        can be determined from stats.
        """
        rule = {}
        for val in stats[feature]:
            rule[val] = stats[feature][val].argMax()
        return rule

    def apply_rule(self, x):
        '''Assigns class label based on value of feature'''
        return self.value_to_label[x[self.feature]]

    def predict(self, X):
        return [self.apply_rule(x) for x in X]

    def predict_proba(self, X):
        raise Exception("Unsupported operation")



