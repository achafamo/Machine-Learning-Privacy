from classifiers.decision_tree import DecisionTree, SPLIT_INFO_GAIN, SPLIT_MAX, SPLIT_GINI
from classifiers.decision_tree_private import DecisionTreePrivate, CONTINUOUS_FRIEDMAN, CONTINUOUS_NEW
from data.util import load_data, split
import logging
import logging.config
logging.config.fileConfig('logging.conf')

def main():

    # load .arff file
    X,y,meta = load_data('spambase.numeric.arff')

    # split into train/test    
    trainX, trainY, testX, testY = split(X,y)

    params = dict(depth=3, splitter=SPLIT_MAX, split_real=True)
    # params = dict(depth=4)

    # NON-PRIVATE

    # initialize classifier
    classifier = DecisionTree(**params)

    # train it
    classifier.train(trainX, trainY, meta=meta)

    # compute accuracy on train and test data
    print '-'*80
    print "Non-Private"
    # classifier.printDiagnostics(depth=1)
    print "Accuracy on train data: {:.2%}".format(classifier.accuracy(trainX, trainY))
    print "Accuracy on test data: {:.2%}".format(classifier.accuracy(testX, testY))
    classifier.printDiagnostics(1)
    print '-'*80

    # PRIVATE, v1

    params['continuous'] = CONTINUOUS_FRIEDMAN

    # initialize classifier
    classifier = DecisionTreePrivate(**params)

    # train it
    classifier.train(trainX, trainY, meta=meta, epsilon=1)

    # compute accuracy on train and test data
    print '-'*80
    print "Private w/ old continuous split"
    # classifier.printDiagnostics(depth=1)
    print "Accuracy on train data: {:.2%}".format(classifier.accuracy(trainX, trainY))
    print "Accuracy on test data: {:.2%}".format(classifier.accuracy(testX, testY))
    classifier.printDiagnostics(1)
    print '-'*80

    # PRIVATE, v2

    params['continuous'] = CONTINUOUS_NEW

    # initialize classifier
    classifier = DecisionTreePrivate(**params)

    # train it
    classifier.train(trainX, trainY, meta=meta, epsilon=1)

    # compute accuracy on train and test data
    print '-'*80
    print "Private w/ new continuous split"
    # classifier.printDiagnostics(depth=1)
    print "Accuracy on train data: {:.2%}".format(classifier.accuracy(trainX, trainY))
    print "Accuracy on test data: {:.2%}".format(classifier.accuracy(testX, testY))
    classifier.printDiagnostics(1)
    print '-'*80

if __name__ == "__main__":
    main()
