import numpy as np
import unittest
from classifiers.decision_tree import DecisionTree, SPLIT_MAX
from classifiers.decision_tree_private import DecisionTreePrivate
from data import util

__author__ = 'mhay@colgate.edu'

DATASET_1 = """@relation test
@attribute x real
@attribute class {+, -}

@data
3, -
10, +
"""

DATASET_2 = """@relation test
@attribute x real
@attribute class {+, -}

@data
5, -
5, -
5.5, -
7, +
7, -
7, -
10, +
12, +
"""



class DecisionTreeTests(unittest.TestCase):

    def test_max_continuous1(self):
        X, y, meta = util.load_data_from_string(DATASET_1)
        tree = DecisionTreePrivate(splitter=SPLIT_MAX, split_real=True)
        (left, right, scores) = tree.score_continuous_splits(X, y, 'x', tree.max_operator_from_counts)
        (exp_left, exp_right, exp_scores) = ([2, 3, 10], [3, 10, 11], [1, 2, 1])
        self.assertEquals(left, exp_left)
        self.assertEquals(right, exp_right)
        self.assertEquals(scores, exp_scores)

    def test_max_continuous2(self):
        X, y, meta = util.load_data_from_string(DATASET_2)
        tree = DecisionTreePrivate(splitter=SPLIT_MAX, split_real=True)
        (left, right, scores) = tree.score_continuous_splits(X, y, 'x', tree.max_operator_from_counts)
        (exp_left, exp_right, exp_scores) = ([4, 5, 5.5, 7, 10, 12], [5, 5.5, 7, 10, 12, 13], [5, 5, 6, 7, 6, 5])
        self.assertEquals(left, exp_left)
        self.assertEquals(right, exp_right)
        self.assertEquals(scores, exp_scores)

    def test_em_scores1(self):
        tree = DecisionTreePrivate()
        # intervals are: [2,3), [3, 10) with scores 1 and 2 respectively
        (left, right, scores) = ([2, 3], [3, 10], [1, 2])
        tree.epsilon = 2
        tree.sensitivity = 1
        scores = tree.em_scores(left, right, scores)
        # expected scores: [exp(1) * 1, exp(2) * 7] and then normalized
        # >>> x = np.array([math.exp(1), math.exp(2)*7])
        # >>> x / x.sum()
        # [ 0.04993017,  0.95006983]
        exp_scores = [0.04993017,  0.95006983]
        np.testing.assert_array_almost_equal(scores, exp_scores)

    def test_em_scores2(self):
        """Same as previous but w/ epsilon different
        """
        tree = DecisionTreePrivate()
        (left, right, scores) = ([2, 3], [3, 10], [1, 2])
        tree.epsilon = 1
        tree.sensitivity = 1
        scores = tree.em_scores(left, right, scores)
        # expected scores: [exp(1./2) * 1, exp(1) * 7] and then normalized
        # >>> x = np.array([math.exp(1./2), math.exp(1)*7])
        # >>> x / x.sum()
        # [ 0.07973815,  0.92026185]
        exp_scores = [0.07973815,  0.92026185]
        np.testing.assert_array_almost_equal(scores, exp_scores)

    def test_em_scores3(self):
        """Same as previous but w/ sensitivity different
        """
        tree = DecisionTreePrivate()
        (left, right, scores) = ([2, 3], [3, 10], [1, 2])
        tree.epsilon = 1
        tree.sensitivity = 5
        scores = tree.em_scores(left, right, scores)
        # expected scores: [math.exp(1./10) * 1, math.exp(2./10) * 7] and then normalized
        # >>> x = np.array([math.exp(1./10) * 1, math.exp(2./10) * 7])
        # >>> x / x.sum()
        # [ 0.11446629,  0.88553371]
        exp_scores = [0.11446629,  0.88553371]
        np.testing.assert_array_almost_equal(scores, exp_scores)

if __name__ == "__main__":
    unittest.main()

