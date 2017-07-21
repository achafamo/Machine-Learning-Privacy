from classifiers.decision_tree import SPLIT_MAX
from classifiers.decision_tree_private import DecisionTreePrivate
from data.util import load_data, split
from harness.execution import ExperimentLauncher


def experiment_fn(dataset_name, depth, epsilon, ntrials):
    X, y, meta = load_data(dataset_name)

    # split into train/test
    trainX, trainY, testX, testY = split(X,y)

    # initialize classifier
    tree = DecisionTreePrivate(splitter=SPLIT_MAX, depth=depth)

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
    datasets = ['adult.arff', 'spambase.arff'] #['adult.arff', 'spambase.arff']
    depths = [1, 5, 10, 20, 25]
    epsilons = [1.0]
    trials = [5]

    args = ('dataset_name', 'depth', 'epsilon', 'trials')
    arg_spaces = dict(zip(args, [datasets, depths, epsilons, trials]))
    print "arg_spaces", arg_spaces

    launcher = ExperimentLauncher('test', experiment_fn, args, arg_spaces, run_local=True)
    # launcher.clear_results()  # overwrite cache
    df = launcher.launch()

    # you can also retrieve the stored results by doing this:
    # from harness.data_store import DataStore
    # df = DataStore('experiments/store', 'test', ('dataset_name', 'depth', 'epsilon', 'trials')).retrieve()

    # goal: dataframe w/ a depth column and then a column representing test_acc for each dataset
    grouped = df.groupby(['dataset_name', 'depth'])['test_acc']
    data = grouped.agg([('avg_test_acc', 'mean'), ('std_test_acc', 'std')])
    data = data.reset_index().pivot('depth', 'dataset_name').reset_index()
    print data
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1,1)
    data.plot('depth', 'avg_test_acc', yerr='std_test_acc', ax=ax)
    plt.savefig('tree_depth.pdf')