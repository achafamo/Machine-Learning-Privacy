import os
import numpy
import csv
from classifiers.classifier import Classifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer as DV
from sklearn.svm import LinearSVC
from data.util import load_data, MetaData


class PPH(Classifier):
	'''
	Runs the synthetic dataset method present in:


	S. A. Vinterbo. Differentially Private Projected Histograms: 
	Construction and Use for Prediction. Proc. ECML-PKDD 2012, 
	to appear.

	After the new dataset is producted we run normal logistic regression 
	'''

	def __init__(self, log = True):
		if log:
			self.model = LogisticRegression()
		else:
			self.model = LinearSVC()

	# def convertData(self, X):
	# 	'''
	# 	Given a dataset convert the dictionary entries in the correct form
	# 	for logisitic regression
	# 	'''
	# 	newX = []
	# 	for datum in X:
	# 		entry = []
	# 		for f in self.features:
	# 			entry.append(datum[f])
	# 		newX.append(entry)
	# 	return newX

	def getClasses(self, data):
		classes = []
		for d in data:
			d = d.strip()
			if float(d[-1]) not in classes:
				classes.append(float(d[-1]))
		classes.sort()
		return classes

	def train(self, X, y, meta=None, epsilon=1.0):

		self.features = meta.features
		self.epsilon = epsilon
		self.classes = sorted(meta.classes)
		# set up the csv file for the R program

		f = open('data.csv', 'w')
		wr = csv.writer(f)

		# write the features
		wr.writerow(self.features + ["labels"])


		# write the data for each entry
		for i in range(len(X)):
			data = []
			for feat in self.features:
				data.append(X[i][feat])
			# add the label to the end
			data.append(y[i])

			# write the entry to the csv file
			wr.writerow(data)
		f.close()

		# call the R program with the file and given epsilon
		os.system("Rscript ./classifiers/pph_logistic.R data.csv " + str(epsilon) + " >& /dev/null")

		# open the output file with new dataset
		X,y,meta = load_data('newdata.arff')

		y = [label[1:-1] for label in y]

		self.vector = DV(sparse=False)
		X = self.vector.fit_transform(X).tolist()
		features = self.vector.get_feature_names()

		newFeatures = []
		for f in features:
			newFeatures.append((f, "real"))

		self.features = newFeatures
		

		y = [self.classes.index(item) for item in y]

		# run logistic regression on the new data
		self.model = self.model.fit(X, y)


		# remove files created during function
		os.remove('newdata.arff')
		os.remove('data.csv')



	def predict(self, X):
		X = self.vector.transform(X)
		prediction = self.model.predict(X)
		# print [self.classes[x] for x in prediction]
		return [self.classes[x] for x in prediction]

	def predict_proba(self, X):
		raise Expection("Unsupported operation")







