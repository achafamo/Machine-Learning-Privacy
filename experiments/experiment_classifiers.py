from classifiers.privateERMLog import PrivERMLog
from classifiers.pph import PPH 
# from classifiers.logistic_private import LogisticPrivate
from data.util import load_data, split
from harness.execution import ExperimentLauncher

def experiment_fn(dataset_name, log, epsilon, ntrials):

	# load the data
	X, y, meta = load_data(dataset_name)

	# split into train/test
	trainX, trainY, testX, testY = split(X,y)

	# initialize classifier
	c = PrivERMLog()

	results = []

	for trial in range(ntrials):
		# train the classifier
		c.train(trainX, trainY, meta=meta, epsilon=epsilon)
		# compute accuracy on train and test data
		train_acc = c.accuracy(trainX, trainY)
		test_acc = c.accuracy(testX, testY)

		results.append( {'trial': trial+1, 'train_acc': train_acc, 'test_acc': test_acc} )

	
	return results


def main():
	# classifiers = [PrivERMLog, PPH]
	datasets = ['adult.arff', 'bank.arff', 'US.arff', 'BR.arff']
	log = [True]

	epsilons = [.1, 0.5, 0.75, 1.0]
	trials = [5]

	args = ('dataset_name', 'log', 'epsilons', 'trials')
	arg_spaces = dict(zip(args, [datasets, log, epsilons, trials]))
	print "arg_spaces", arg_spaces

	launcher = ExperimentLauncher('test', experiment_fn, args, arg_spaces, run_local=False)
	launcher.clear_results()
	df = launcher.launch()

	print df

	grouped = df.groupby(['dataset_name', 'epsilons'])['test_acc']
	data = grouped.agg([('avg_test_acc', 'mean'), ('std_test-acc', 'std')])
	data = data.reset_index().pivot('epsilons', 'dataset_name').reset_index()
	print data

	import matplotlib.pyplot as plt

	fig, ax = plt.subplots(1,1)
	data.plot('epsilons', 'avg_test_acc', yerr='std_test-acc', ax=ax)
	plt.savefig('classifier.pdf')










