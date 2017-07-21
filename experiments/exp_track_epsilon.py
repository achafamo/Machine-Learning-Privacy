from classifiers.decision_tree import SPLIT_MAX
from classifiers.decision_tree_private import DecisionTreePrivate
from data.util import load_data, split
from harness.execution import ExperimentLauncher
from data.makeSynthetic import main_, addRandom

def experiment_fn(dataset_name, track_epsilon, epsilon, ntrials):
   
    X, y, meta = load_data(dataset_name)

    # split into train/test
    trainX, trainY, testX, testY = split(X,y)

    # initialize classifier
    tree = DecisionTreePrivate(splitter=SPLIT_MAX, depth = 10, track_epsilon = True)

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
    datasets = ['adult.arff','bank.arff', 'ds1.10.arff']
    track_epsilon = [True, False]    
    epsilons = [1.0]
    trials = [10]

    args = ('dataset_name', 'track_epsilon', 'epsilon', 'trials')
    arg_spaces = dict(zip(args, [datasets, track_epsilon, epsilons, trials]))
    print "arg_spaces", arg_spaces

    launcher = ExperimentLauncher('test', experiment_fn, args, arg_spaces, run_local=False)
    launcher.clear_results()  # overwrite cache
    df = launcher.launch()
    #output = open('output_track_epsilon.csv', 'w')
    #df.to_csv(output)
    #print df 
    grouped = df.groupby(['dataset_name', 'track_epsilon'])['test_acc']
    data = grouped.agg([('avg_test_acc', 'mean'), ('std_test_acc', 'std')])
    data = data.reset_index().pivot('track_epsilon', 'dataset_name').reset_index()
    output = open('output_track_epsilon.csv', 'w')
    data.to_csv(output)
    print 'data'
    print data