import logging
from classifiers.onerule import OneRule
import diffp

__author__ = 'mhay'

class OneRulePrivate(OneRule):

    def train(self, X, y, meta=None, epsilon=None):
        # for each feature, for each value, distribution over labels
        # rule: for each feature value, assignment to label
        # how many possible rules?  #features * #values ** #labels
        # algorithm ideas:
        # 1. use EM to pick best rule (quality function is -error), then use EM to build rule
        # 2. use EM to sample from set of all possible rules
        # 3. like 1 but reverse steps
        self._set_epsilon(epsilon)
        super(OneRulePrivate,self).train(X, y, meta)

    def _pick_best(self, stats):
        #todo: this computes error for feature values in active domain (i.e., occur in training data)
        #todo: but for diffp we should really do this for all possible feature values
        errors = self._compute_error(stats)
        best = errors.argMin()
        features, errors = zip(*errors.items())
        quality = [-error for error in errors]  # quality score is -error
        feature = diffp.e_m_scores(features, quality, 1, self.epsilon/2)
        logging.debug('best feature={0} we sampled={1}'.format(best, feature))
        return feature

    def _make_rule(self, feature, stats):
        """Rule is a map from feature value to majority label, which
        can be determined from stats.
        """
        val_to_dist = stats[feature]
        k = len(val_to_dist)
        eps_budget = self.epsilon/(2 * k)
        rule = {}
        for val in val_to_dist:
            labels, counts = zip(*val_to_dist[val].items())
            best = val_to_dist[val].argMax()
            label = diffp.e_m_scores(labels, counts, 1, eps_budget)
            rule[val] = label
            logging.debug('For val={0} best={1} we sampled={2}'.format(val, best, label))
        return rule

    def _set_epsilon(self, epsilon):
        self.epsilon = epsilon