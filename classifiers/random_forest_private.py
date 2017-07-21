import random
import math
from classifiers.random_tree import RandomTree
from classifiers.classifier import Classifier


class RandomForestPrivate(Classifier):

	def __init__(self, attr_min=-100, attr_max=100, h=6):
		self.attr_min = attr_min
		self.attr_max = attr_max
		self.height = h

	def train(self, X, y, meta=None, epsilon=None):
		self.features = meta.features
		self.n = len(X) # number of data points
		self.num_trees = int(math.log(self.n))
		self.epsilon = epsilon


		# build the forest
		forest = []
		for i in range(self.num_trees):
			tree = RandomTree(num_trees=self.num_trees, epsilon=self.epsilon)
			tree.train(X, y, meta)
			forest.append(tree)

		self.forest = forest

	def predict(self, X):
		final_prediction = []
		for d in X:
			prediction = []
			for tree in self.forest:
				prediction = prediction + tree.predict([d])
			probability = 0
			for n in prediction:
				probability += float(n)
			probability /= self.num_trees
			r = random.random()
			if r <= probability:
				final_prediction.append("1")
			else:
				final_prediction.append("0")
		return final_prediction


	def predict_proba(self, X):
		raise Expection("Unsupported operation")





