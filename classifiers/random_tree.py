import random
import math
import util
import diffp

from classifiers.decision_tree import DecisionTree, SPLIT_RANDOM


class RandomTree(DecisionTree):
	def __init__(self, num_trees=None, epsilon=None):
		self.num_tree = num_trees
		self.epsilon = epsilon
		super(self.__class__, self).__init__(splitter=SPLIT_RANDOM)

	def predict_proba(self, X):
		num_pos = diffp.noisy_count(traingingLabels.count("1"), self.epsilon/self.num_tree)
		num_neg = diffp.noisy_count(traingingLabels.count("0"), self.epsilon/self.num_tree)
		if num_pos < 0 or num_neg < 0 or (num_pos == 0 and num_neg == 0):
			return random.random()
		else:
			return num_pos/(num_pos + num_neg)
