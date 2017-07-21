import unittest
import diffp
import util

__author__ = 'mhay@colgate.edu'


# todo: write test cases for critical diffp functions
class DecisionTreeTests(unittest.TestCase):

    def test_compute_unnormalized_scores(self):
        """Test the math by systematically varying all three parameters"""
        # todo: implement this test!
        pass

    def many_samples(self, prob):
        trials = 10000
        counts = util.Counter()
        for _ in range(trials):
            counts[diffp.sample(prob)] += 1
        counts.normalize()
        return counts

    def test_sample(self):
        """Test random sampling by sampling a large number (say 10000) samples and making sure
        that distribution matches what you'd expect.  Test corner cases.
        """
        dist = self.many_samples([0, 0, 0, 1])
        self.assertEquals(3, dist.argMax())

        dist = self.many_samples([1, 0, 0, 0, 0])
        self.assertEquals(0, dist.argMax())

        dist = self.many_samples([0.5, 0, 0, 0.25, 0.25])
        self.assertAlmostEquals(dist[0], 0.5, delta=0.01)
        self.assertAlmostEquals(dist[3], 0.25, delta=0.01)
        self.assertAlmostEquals(dist[4], 0.25, delta=0.01)
        self.assertEquals(dist[1], 0)
        self.assertEquals(dist[2], 0)

        with self.assertRaises(AssertionError):
            diffp.sample([0.5, 0.5, 0.01])
