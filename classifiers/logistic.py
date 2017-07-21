import math
import numpy

from classifiers.classifier import Classifier
from sklearn.linear_model import LogisticRegression

class Logistic(Classifier):

	def __init__(self):
		self.model = LogisticRegression()


	def convertData(self, X):
		'''
		Given a dataset convert the dictionary entries in the correct form
		for logisitic regression
		'''
		newX = []
		for datum in X:
			entry = []
			for f in self.features:
				entry.append(datum[f])
			newX.append(entry)
		return newX


	def train(self, X, y, meta=None):
		'''
		Trains the given dataset with logisitic regression on training data
		X with labels y. meta, if available, contains metadata about the 
		dataset (such as number of features, feature types, etc.
		'''
		self.features = meta.features
		X = self.convertData(X)
		self.model = self.model.fit(X, y)


	def predict(self, X):
		prediction = self.model.predict(self.convertData(X))
		return [str(int(x)) for x in prediction]

	def predict_proba(self, X):
		raise Expection("Unsupported operation")



