from classifiers.decision_tree import SPLIT_MAX
from classifiers.decision_tree_private import DecisionTreePrivate, CONTINUOUS_NEW, CONTINUOUS_FRIEDMAN
from data.util import load_data, split
from harness.execution import ExperimentLauncher
import pandas

def experiment_fn(dataset_name, continuous, epsilon, ntrials):
    X, y, meta = load_data(dataset_name)

    # split into train/test
    trainX, trainY, testX, testY = split(X,y)

    # initialize classifier
    tree = DecisionTreePrivate(splitter=SPLIT_MAX, continuous = continuous)

    results = []
    for trial in range(ntrials):

        # train it
        tree.train(trainX, trainY, meta=meta, epsilon=epsilon)

        # compute accuracy on train and test data
        train_acc = tree.accuracy(trainX, trainY)
        test_acc = tree.accuracy(testX, testY)

        results.append( {'trial': trial+1, 'train_acc': train_acc, 'test_acc': test_acc} )

    return results


def main():
    datasets = ['spambase.numeric.arff', 'optdigits.arff', 'skin.arff']
    continuous = [CONTINUOUS_NEW, CONTINUOUS_FRIEDMAN]
    epsilons = [1.0]
    trials = [5]

    args = ('dataset_name', 'continuous', 'epsilon', 'trials')
    arg_spaces = dict(zip(args, [datasets, continuous, epsilons, trials]))
    print "arg_spaces", arg_spaces

    launcher = ExperimentLauncher('test_continuous', experiment_fn, args, arg_spaces, run_local=False)
    launcher.clear_results()  # overwrite cache
    df = launcher.launch()
   
    #output = open('output_Continuous.csv', 'w')
    #df.to_csv(output_Continuous)
    # you can also retrieve the stored results by doing this:
    #from harness.data_store import DataStore
    #df = DataStore('experiments/store', 'test', ('dataset_name', 'continuous', 'epsilon', 'trials')).retrieve()
    #print 'printing df'
    #print df

    # goal: dataframe w/ a depth column and then a column representing test_acc for each dataset
    grouped = df.groupby(['dataset_name', 'continuous'])['test_acc']
    data = grouped.agg([('avg_test_acc', 'mean'), ('std_test_acc', 'std')])
    data = data.reset_index().pivot('continuous', 'dataset_name').reset_index()
    output = open('output_Continuous.csv', 'w')
    data.to_csv(output)
    print 'data'
    print data
    # import matplotlib.pyplot as plt
    # fig, ax = plt.subplots(1,1)
    # data.plot('depth', 'avg_test_acc', yerr='std_test_acc', ax=ax)
    # plt.savefig('tree_depth.pdf')