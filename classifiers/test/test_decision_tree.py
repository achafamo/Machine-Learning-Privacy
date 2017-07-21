import unittest
from classifiers.decision_tree import DecisionTree
from data import util

__author__ = 'mhay@colgate.edu'

DATASET_1 = """@relation test
@attribute a {lo, hi}
@attribute b {down, up}
@attribute class {+, -}

@data
lo, down, -
hi, down, -
lo, up, +
lo, up, +
hi, down, -
hi, up, +
hi, up, +
"""

DATASET_2 = """@relation test
@attribute x real
@attribute class {+, -}

@data
5, -
5, -
6, -
7, +
7, -
7, -
8, +
15, +
"""

class DecisionTreeTests(unittest.TestCase):

    def example1(self):
        return self.load_example(DATASET_1)

    def example2(self):
        return self.load_example(DATASET_2)

    def load_example(self, d):
        X, y, meta = util.load_data_from_string(d)
        tree = DecisionTree()
        tree.meta = meta
        return (X, y, tree)

    def test_entropy(self):
        tree = DecisionTree()
        self.assertAlmostEquals(tree.entropy([1, 0, 0, 1, 1, 0]), 1)
        self.assertAlmostEquals(tree.entropy([1]*10), 0)
        # 4 a, 1 b, 2 c:
        # >>> log2 = lambda x: math.log(x, 2)
        # >>> -1 * ( 4./7 * log2(4./7) + 2./7 * log2(2./7) + 1./7 * log2(1./7) )
        self.assertAlmostEquals(tree.entropy(['a', 'b', 'a', 'a', 'c', 'c', 'a']), 1.3787834934861756)

        # 2 a, 1 b:
        # >>> log2 = lambda x: math.log(x, 2)
        # >>> -1 * (2./3 * log2(2./3) + 1./3 * log2(1./3))
        self.assertAlmostEquals(tree.entropy(['a', 'b', 'a']), 0.9182958340544896)

        # 4 +, 3 -:
        # >>> log2 = lambda x: math.log(x, 2)
        # >>> -1 * (4./7 * log2(4./7) + 3./7 * log2(3./7))
        self.assertAlmostEquals(tree.entropy(['+']*4 + ['-']*3), 0.9852281360342516)

    def test_info_gain(self):
        X, y, tree = self.example1()
        # splitting on attribute 'a':
        # lo split has 3 instances with a 2/3 to 1/3 split, w/ entropy = 0.9182958340544896
        # hi split has 4 instances with a 1/2 to 1/2 split, w/ entropy = 1.0
        # thus info gain score is:
        # >>> log2 = lambda x: math.log(x, 2)
        # >>> (2. * log2(2./3) + 1. * log2(1./3)) + (2. * log2(2./4) + 2. * log2(2./4))
        self.assertAlmostEquals(tree.info_gain(X, y, 'a'), -6.754887502163469)

    def test_info_gain2(self):
        # splitting on attribute 'b':
        # b perfectly classifies the data, thus IG is maximized
        # down split has 3 instances with a 0/3 to 3/3 split, w/ entropy = 0
        # up split has 4 instances with a 4/4 to 0/4 split, w/ entropy = 0
        # thus info gain score is:
        # >>> log2 = lambda x: math.log(x, 2)
        # >>> (3. * log2(3./3) + 0.) + (4. * log2(4./4) + 0)
        X, y, tree = self.example1()
        self.assertAlmostEquals(tree.info_gain(X, y, 'b'), 0.0)
        #todo: add more tests

    def test_info_gain_continuous(self):
        X, y, tree = self.example2()

        # based on a visual inspection, splitting at x <= 7 has lowest entropy
        # splitting on x <= 7:
        # x <= 7 has 6 instances with a 5./6 to 1./6 split
        # x > 7 has 2 instances with a 0./2 to 2./2 split
        # thus info gain score is:
        # >>> log2 = lambda x: math.log(x, 2)
        # >>> (5. * log2(5./6) + 1. * log2(1./6)) + (0. + 2. * log2(2./2))
        # -3.900134529890125

        # a plausible alternative is splitting on x <= 6
        # splitting on x <= 6:
        # x <= 6 has 3 instances with a 3./3 to 0./6 split
        # x > 6 has 5 instances with a 2./5 to 3./5 split
        # thus info gain score is:
        # >>> log2 = lambda x: math.log(x, 2)
        # >>> (3. * log2(3./3) + 0) + (2. * log2(2./5) + 3. * log2(3./5))
        # -4.854752972273343
        # notice that this is lower and therefore a less good split
        gain, val = tree.info_gain_continuous(X, y, 'x')
        self.assertEquals(gain, -3.900134529890125)

    def test_max_operator(self):
        X, y, tree = self.example1()
        self.assertEquals(tree.max_operator(X, y, 'a'), 2+2)

    def test_gini_index(self):
        X, y, tree = self.example1()
        # low is 3/7, with distribution [1/3, 2/3]
        # hi is 4/7, with distribution [1/2, 1/2]
        # >>> -1 * (3. * (1 - ((1./3)**2 + (2./3)**2)) + 4. * (1 - ((1./2)**2 + (1./2)**2)))
        self.assertEquals(tree.gini_index(X, y, 'a'), -3.333333333333333)



if __name__ == "__main__":
    unittest.main()

