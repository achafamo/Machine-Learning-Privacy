import unittest
from classifiers.onerule_private import OneRule
from data.util import load_data


class OneRuleTests(unittest.TestCase):

    def testTrain(self):
        X, y, meta = load_data('weather.arff')  #todo:write function to load from string so I can make custom dataset for testing
        one_rule = OneRule()
        one_rule.train(X, y, meta=meta)
        self.assertEquals(one_rule.feature, 'humidity')


if __name__ == "__main__":
    unittest.main()
