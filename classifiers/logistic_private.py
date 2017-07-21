
import logging
import gupt
import hashlib
import time 
import math
import numpy
import os
import sys
import random
from classifiers.logistic import Logistic
from sklearn.linear_model import LogisticRegression
from datadriver.datadriver import GuptDataDriver
from computedriver.computedriver import GuptComputeDriver
from data.util import MetaData
from sklearn.feature_extraction import DictVectorizer as DV




# helper classes
class ClassifierDataDriver(GuptDataDriver):
	'''
	This parses a list of lists for the gupt program.
	'''

	def set_data_source(self, *fargs):
		self.data = fargs[0]
		self.labels = fargs[1]
		self.place = 0

	def create_record(self):
		if self.place < len(self.data):
			# return the next record
			record = (self.data[self.place], self.labels[self.place])
			self.place += 1	
			return record
		return None

class LogComputeDriver(GuptComputeDriver):
	'''
	Computer driver used by the gupt file to run logistic regression
	'''
	numFeatures = None

	def initialize(self):
		self.records = []
		self.labels = []

	def execute(self, record):
		if not record:
			return
		data, label = record

		# accumulate data records for logistic regression
		self.records.append(data)
		self.labels.append(label)

	def finalize(self):
		# run logistic regression
		model = LogisticRegression()
		model = model.fit(self.records, self.labels)
		# get the fitted model
		coeffients = [model.intercept_.tolist()[0]] + model.coef_.tolist()[0]
		# return the coeffients
		return [float(x) for x in coeffients]

	def get_output_bounds(self, first_quartile=None, third_quartile=None):
		assert LogComputeDriver.numFeatures != None
		if not first_quartile or not third_quartile:
			return [-10.0]*LogComputeDriver.numFeatures, [10.0]*LogComputeDriver.numFeatures
		return first_quartile, third_quartile


class LogisticPrivate(Logistic):

	# def getClasses(self, data):
	# 	classes = []
	# 	for d in data:
	# 		d = d.strip()
	# 		if float(d[-1]) not in classes:
	# 			classes.append(float(d[-1]))
	# 	classes.sort()
	# 	return classes


	def train(self, X, y, meta=None, epsilon=1.0, blocker="NaiveDataBlocker"):

		self.vector = DV(sparse=False)
		X = self.vector.fit_transform(X).tolist()
		features = self.vector.get_feature_names()

		newFeatures = []
		for f in features:
			newFeatures.append((f, "real"))

		meta = MetaData(newFeatures, meta._classes)
		self.features = meta.features
		self.classes = sorted(meta.classes)

		# set up the labels
		newY = []
		for label in y:
			newY.append(self.classes.index(label))

		# set up the reader
		reader = ClassifierDataDriver()
		reader.set_data_source(X,newY)


		reader.set_sensitiveness([True]*(len(self.features)+1))

		# train using the data
		LogComputeDriver.numFeatures = len(self.features) + 1
		runtime = gupt.GuptRunTime(LogComputeDriver, reader, epsilon, blocker_name=blocker, blocker_args=2)
		results = runtime.start_windsorized()
		assert len(results) == len(self.features) + 1

		# set the model
		self.model.coef_ = numpy.array(results[1:],ndmin=2)
		self.model.intercept_ = numpy.array(results[0],ndmin=1)
		self.model.classes_ = numpy.array(self.classes)



	def predict(self, X):
		X = self.vector.transform(X)
		prediction = self.model.predict(X).tolist()
		return  prediction #[self.classes[x] for x in prediction]

	def predict_proba(self, X):
		raise Expection("Unsupported operation")

