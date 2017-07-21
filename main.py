from classifiers.decision_tree import DecisionTree, SPLIT_INFO_GAIN, SPLIT_MAX, SPLIT_GINI
from classifiers.random_forest_private import RandomForestPrivate
from classifiers.privateERMLog import PrivERMLog
from data.util import load_data, split
from classifiers.pph import PPH
import logging
import logging.config
logging.config.fileConfig('logging.conf')

def main():

    # load .arff file
    X,y,meta = load_data('adult.arff')

    # split into train/test    
    trainX, trainY, testX, testY = split(X,y)

    # initialize classifier
    classifier =  PrivERMLog() # DecisionTree(splitter=SPLIT_GINI, split_real=True)

    # train it
    classifier.train(trainX, trainY, meta=meta, epsilon=10.0)
    # classifier.printDiagnostics()

    # compute accuracy on train and test data
    print "Accuracy on train data: {:.2%}".format(classifier.accuracy(trainX, trainY))
    print "Accuracy on test data: {:.2%}".format(classifier.accuracy(testX, testY))


if __name__ == "__main__":
    main()
