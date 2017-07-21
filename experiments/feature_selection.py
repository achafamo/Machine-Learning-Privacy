from classifiers.decision_tree import DecisionTree, SPLIT_INFO_GAIN, SPLIT_MAX, SPLIT_GINI
from classifiers.decision_tree_private import DecisionTreePrivate, CONTINUOUS_FRIEDMAN, CONTINUOUS_NEW
from data.util import load_data, split
import logging
import logging.config
from data.makeSynthetic import main_, addRandom
logging.config.fileConfig('logging.conf')

def main():

    # load .arff file
    dataset = 'US'
    for i in range(10):
        print i*10

        X,y,meta = load_data(dataset+ '.arff')

        # split into train/test    
        trainX, trainY, testX, testY = split(X,y)

        params = dict(depth=5, splitter=SPLIT_GINI, split_real=True, select_features = False)
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
        #classifier.printDiagnostics(1)
        print '-'*80

        # PRIVATE, v1

        
        # initialize classifier
        classifier = DecisionTreePrivate(**params)

        # train it
        classifier.train(trainX, trainY, meta=meta, epsilon=1)

        # compute accuracy on train and test data
        print '-'*80
        print "Private w/ no feature selection implemented"
        # classifier.printDiagnostics(depth=1)
        print "Accuracy on train data: {:.2%}".format(classifier.accuracy(trainX, trainY))
        print "Accuracy on test data: {:.2%}".format(classifier.accuracy(testX, testY))
        #classifier.printDiagnostics(1)
        print '-'*80

        # PRIVATE, v2

        params['select_features'] = True

        # initialize classifier
        classifier = DecisionTreePrivate(**params)

        # train it
        classifier.train(trainX, trainY, meta=meta, epsilon=1)

        # compute accuracy on train and test data
        print '-'*80
        print "Private w/ feature selection implemented"
        # classifier.printDiagnostics(depth=1)
        print "Accuracy on train data: {:.2%}".format(classifier.accuracy(trainX, trainY))
        print "Accuracy on test data: {:.2%}".format(classifier.accuracy(testX, testY))
        #classifier.printDiagnostics(1)
        print '-'*80
        main_('data/'+ dataset, i*10)
        dataset = (dataset+ '_new')

if __name__ == "__main__":
    main()
