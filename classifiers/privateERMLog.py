import os
import numpy
import time
from classifiers.classifier import Classifier
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer as DV
from sklearn.svm import LinearSVC
from data.util import MetaData

class PrivERMLog(Classifier):
	'''
	Runs the logistic regression version of the PrivateERM algorithms
	as detailed in:

	Kamalika Chaudhuri, Claire Monteleoni and Anand Sarwate, 
	Differentially Private Empirical Risk Minimization, 
	Journal of Machine Learning Research, 2011.

	'''

	def __init__(self, regularization=0.01, log=True, huber=0.5):

		self.log = log # selects between logistic regression and SVM 
		if self.log:
			self.model = LogisticRegression()
		else:
			self.model = LinearSVC()
		self.regularization = regularization
		self.huber = huber

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


	def formatFile(self, X, y):
		# set up the file to pass into logistic regression code

		# generate unique file name
		filename = "data" + str(time.time()) + ".txt"
		f = open(filename, 'w')
		# first line: n (number of training points)
		f.write(str(float(len(X))) + '\n')    
		# second line: d (dimensionality)
		f.write(str(float(len(X[0]))) + '\n')
		# third line: lambda (regularization parameter)
		f.write(str(float(self.regularization)) + '\n')
		# fourth line: epsilon (privacy parameter)
		f.write(str(float(self.epsilon)) + '\n')

		# fifth line: huber constant (only for SVM)
		if not self.log:
			f.write(str(self.huber) + '\n')


		for d in X:
			# write the data to the file
			d = [str(x) for x in d]
			f.write(" ".join(d) + '\n')

		# write the label to the file


		for label in y:
			if self.classes[0] == label:
				f.write("-1")
			else:
				f.write(label)
			f.write("\n")

		# close the file
		f.close()

		# return name of data file
		return filename


	def train(self, X, y, meta=None, epsilon=1.0, objective=True):
		self.epsilon = epsilon
		# X, meta = DictVectorizer(X, meta)

		self.vector = DV(sparse=False)
		X = self.vector.fit_transform(X).tolist()
		features = self.vector.get_feature_names()

		newFeatures = []
		for f in features:
			newFeatures.append((f, "real"))

		meta = MetaData(newFeatures, meta._classes)
		self.features = meta.features
		self.classes = sorted(meta.classes)
		filename = self.formatFile(X, y)
		# compile the source code
		# if self.log:
		# 	os.system("gcc -lm -llbfgs ./thirdparty/PrivERM/PrivateERM/lrsimple.c")
		# else:
		# 	os.system("gcc -lm -llbfgs ./thirdparty/PrivERM/PrivateERM/svmsimple.c")
		
		# generate unique output file name
		outfile = "out" + str(time.time()) + ".txt"

		# run the C code and pipe the output to python
		os.system("./a.out " + filename + " > " + outfile)



		output = open(outfile, 'r')

		# get the coef of output perturbation model
		output.next()

		if objective:
		# get the coef for the objective perturbation model of logistic regression
			output.next()
		coef = output.next()
		coef = coef.split()[:-1]
		coef = [float(x) for x in coef]

		# store the coef to the logistic regression
		self.model.coef_ = numpy.array(coef,ndmin=2)
		self.model.intercept_ = numpy.array(0.0,ndmin=1)
		self.model.classes_ = numpy.array([-1.0, 1.0])

		output.close()
		# remove files created during function
		os.remove(outfile)
		os.remove(filename)
		# os.remove('a.out')


	def predict(self, X):

		
		X = self.vector.transform(X)
		prediction = self.model.predict(X)
		returnPred = []
		for label in prediction:
			if label == -1.0:
				returnPred.append(self.classes[0])
			else:
				returnPred.append(self.classes[1])
		return returnPred

	def predict_proba(self, X):
		raise Expection("Unsupported operation")






		
