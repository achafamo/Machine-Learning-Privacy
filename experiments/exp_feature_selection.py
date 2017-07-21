from classifiers.decision_tree import SPLIT_MAX
from classifiers.decision_tree_private import DecisionTreePrivate
from data.util import load_data, split
from harness.execution import ExperimentLauncher
from data.makeSynthetic import main_, addRandom

def experiment_fn(dataset_name, rand, select_features, epsilon, ntrials):
    dataset = dataset.split('.')[0]
    main_('data/'+ dataset_name, rand)
    dataset = (dataset+ '_new')
    X, y, meta = load_data(dataset_name)

    # split into train/test
    trainX, trainY, testX, testY = split(X,y)

    # initialize classifier
    tree = DecisionTreePrivate(splitter=SPLIT_MAX, depth = 1, select_features = select_features)

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
    datasets = ['adult.arff','adult_new.arff', 'US_new.arff']
    rand = [10,20,30,40,50,60,70,80,90,100]
    select_features = [True, False]
    epsilons = [1.0]
    trials = [1]

    args = ('dataset_name', 'rand',  'select_features', 'epsilon', 'trials')
    arg_spaces = dict(zip(args, [datasets, rand, select_features, epsilons, trials]))
    print "arg_spaces", arg_spaces

    launcher = ExperimentLauncher('test', experiment_fn, args, arg_spaces, run_local=False)
    launcher.clear_results()  # overwrite cache
    df = launcher.launch()
    output = open('output_1.csv', 'w')
    df.to_csv(output)
    print df 