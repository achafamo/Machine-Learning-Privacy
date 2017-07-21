from classifiers.classifier import Classifier
import math
import util
import sys
import random
try:
    from scipy.stats import beta
except ImportError:
    print >>sys.stderr, "Could not import scipy.stats.beta!"

SPLIT_INFO_GAIN = "split criteria: info gain"
SPLIT_MAX = "split criteria: max"
SPLIT_GINI = "split criteria: gini index"
SPLIT_RANDOM = "split criteria: random"

# todo: add more unittests for
# isDone
# stopping conditions
# generateSplit and generateSplitContinuous functions
# gini Index when one or more of the counters is zero (can arise w/ continuous features)


class DecisionNode:
    """
    Helper node class for the decision tree
    """
    def __init__(self):
        self.splitFeature = None
        self.infoGain = None
        self.subTrees = {}
        self.isLeaf = False
        self.label = None

class DecisionTree(Classifier):

    def __init__(self, splitter=SPLIT_INFO_GAIN, depth=3, to_prune=False, split_real=True, select_features= False):
        if splitter == SPLIT_INFO_GAIN:
            self.utility = self.info_gain
            self.utility_continuous = self.info_gain_continuous
        elif splitter == SPLIT_MAX:
            self.utility = self.max_operator
            self.utility_continuous = self.max_operator_continuous
        elif splitter == SPLIT_GINI:
            self.utility = self.gini_index
            self.utility_continuous = self.gini_index_continuous
        elif splitter == SPLIT_RANDOM:
            self.utility = self.random_split
            self.utility_continuous = self.random_split_continuous
        else:
            raise Exception("Unrecognized splitter specified: {0}".format(splitter))
        self.depth = depth
        self.to_prune = to_prune
        self.split_real = split_real   # if False, continuous features are ignored
        self.select_features = select_features

        self.root = None       # train will initialize
        self._meta = None       # train will initialize
        self.currentNode = None  # trainHelper will initialize  #todo: remove this?

    @property
    def meta(self):
        assert self._meta is not None
        return self._meta

    @meta.setter
    def meta(self, m):
        self._meta = m

    # ---------------------------------------------
    # TRAINING FUNCTIONS
    # ---------------------------------------------
    def train(self, X, y, meta=None):
        self.meta = meta
        features = meta.features
        if self.select_features:
            #print features
            features = self.selectFeatures(X, y, features, 10)
            #print features
        if not self.split_real:
            features = [f for f in features if not self.meta.is_real(f)]   # keep only the non-real features
        self.root = self.trainHelper(X, y, features,
                                     self.findPlurality(y), self.depth)
        if self.to_prune:
            self.root = self.prune(self.root)

    def trainHelper(self, trainingData, trainingLabels, features, parent_plurality, depth):
        """Helper function for training with the training data is a recursive function that builds the decision tree.

        Recursive base cases:
        no training data -> take plurality label from parent (need to pass in to function)
        all examples have same class label -> stop building tree and classify using this label
        no more attributes to split on -> label is plurality of examples
        max depth -> label is plurality choice
        """

        newNode = DecisionNode()
        self.currentNode = newNode

        # Check stopping criteria
        if self.isDone(trainingLabels, depth, features):
            newNode.isLeaf = True
            if self.isDataEmpty(trainingData):
                newNode.label = parent_plurality
            else:
                newNode.label = self.assign_label(trainingLabels, depth)
            return newNode

        # Find best feature to split on
        splitFeature = self.findSplitFeature(trainingData, trainingLabels, features)
        if splitFeature not in features:
            splitFeature, splitPoint = splitFeature  # todo: revise this?
        else:
            splitPoint = 0

        newNode.splitFeature = splitFeature
        newNode.splitPoint = splitPoint

        # Recurse:
        # - split the training data into subsets based on the value of the splitFeature
        # - train a decision tree on each subset
        # - assign these trees as children of newNode
        if self.meta.is_real(splitFeature):
            split_data, split_labels = self.generateSplitContinuous(trainingData, trainingLabels, newNode.splitFeature, newNode.splitPoint)
            l = ['less', 'greater']
            for i in range(len(split_data)):
                newFeatures = features[:]
                newFeatures.remove(newNode.splitFeature)
                newNode.subTrees[l[i]] = self.trainHelper(split_data[i], split_labels[i], newFeatures,
                                                          self.findPlurality(trainingLabels),depth-1)
        else:
            values = self.meta.get_values(newNode.splitFeature)
            split_data, split_labels = self.generateSplit(trainingData, trainingLabels, newNode.splitFeature)
            for i in range(len(values)):
                assert values[i] != "", "For some reason the feature value is empty for feature: {0}".format(newNode.splitFeature)
                newFeatures = features[:]
                newFeatures.remove(newNode.splitFeature)
                newNode.subTrees[values[i]] = self.trainHelper(split_data[i], split_labels[i], newFeatures,
                                                               self.findPlurality(trainingLabels), depth - 1)
        return newNode

    def isDataEmpty(self, trainingData):
        return trainingData == []

    def isDone(self, trainingLabels, depth, features):
        return depth <= 0 or features == [] or all(l == trainingLabels[0] for l in trainingLabels)

    def findPlurality(self, trainingLabels):
        count = util.Counter()
        count.incrementAll(trainingLabels, 1)
        return count.argMax()

    def assign_label(self, traingingLabels, depth):
        return self.findPlurality(traingingLabels)

    def findSplitFeature(self, trainingData, trainingLabels, features):
        """
        this method finds the feature to split on based on the utility function specified. For continuous attributes
        it also finds the best split point
        """
        max_score = None
        max_feature = None
        for f in features:
            if self.meta.is_real(f):
                score, splitPoint = self.utility_continuous(trainingData, trainingLabels, f)
            else:
                score = self.utility(trainingData, trainingLabels, f)
            if score >= max_score:
                max_score = score
                if self.meta.is_real(f):
                    max_feature = (f, splitPoint)
                else:
                    max_feature = f
        assert max_feature is not None
        return max_feature
    # ---------------------------------------------
    # (END) TRAINING FUNCTIONS
    # ---------------------------------------------

    # ---------------------------------------------
    # TESTING FUNCTIONS
    # ---------------------------------------------
    def predict(self, data):
        """
        Classifies each datum by passing it through the decision tree.

        Expects data to be a list.  Each datum in list is a feature vector (i.e., a dictionary)
        """
        assert self.root is not None, "Tree was never trained!"
        guesses = []
        for datum in data:
            guesses.append(self.classifyHelper(datum, self.root))
        return guesses

    def classifyHelper(self, datum, node):
        """Recursive helper function that explores the tree to classify the datum
        """
        if node.isLeaf:
            return node.label

        # else recursively travel the tree
        if self.meta.is_real(node.splitFeature):
            splitFeature = node.splitFeature
            splitPoint = node.splitPoint
            if datum[splitFeature] > splitPoint:
                value = 'greater'
            else:
                value = 'less'
        else:
            value = datum[node.splitFeature]           
        return self.classifyHelper(datum, node.subTrees[value])
    # ---------------------------------------------
    # (END) TESTING FUNCTIONS
    # ---------------------------------------------

    # ---------------------------------------------
    # HELPER FUNCTIONS FOR SIMPLE STUFF
    # ---------------------------------------------
    def generateSplit(self, data, labels, f):
        """
        Makes a list of sub-training sets given a feature f to split on
        """
        assert len(data) == len(labels)
        splitData = []
        splitLabels = []
        # make the sub-training set that results from the split
        for v in self.meta.get_values(f):
            data_i = []
            labels_i = []
            for i in range(len(data)):                
                if data[i][f] == v:
                    data_i.append(data[i])
                    labels_i.append(labels[i])
            splitData.append(data_i)
            splitLabels.append(labels_i)
        return (splitData,splitLabels)
    # ---------------------------------------------
    # (END) HELPER FUNCTIONS FOR SIMPLE STUFF
    # ---------------------------------------------

    # ---------------------------------------------
    # DISCRETE FEATURE SELECTION FUNCTIONS
    # ---------------------------------------------
    def info_gain(self, data, labels, f):
        return self.find_best(data, labels, f, self.info_gain_from_counts)

    def max_operator(self, data, labels, f):
        """Returns the number correct if we split on feature f and then predict
        majority class label.
        """
        return self.find_best(data, labels, f, self.max_operator_from_counts)

    def gini_index(self, data, labels, f):
        """Computes gini index as defined in Friedman and Schuster, "Data Mining with Differential Privacy", KDD 2010.
        """
        return self.find_best(data, labels, f, self.gini_index_from_counts)

    def random_split(self, data, labels, f):
        """ Selects a feature at random
        """
        return random.random()

    def find_best(self, data, labels, f, score_fn):
        split_data, split_labels = self.generateSplit(data, labels, f)
        return score_fn(self.make_counters(split_labels))

    def make_counters(self, split_labels):
        counters = []
        for labels in split_labels:
            counter = util.Counter()
            counter.incrementAll(labels, 1)
            counters.append(counter)
        return counters

    def info_gain_from_counts(self, counters):
        """Note: this does NOT compute the info gain.  It instead computes an alternative score.  However, maximizing
        this alternative score is equivalent to maximizing info gain.

        The score is defined in Friedman and Schuster, "Data Mining with Differential Privacy", KDD 2010.
        """
        score = 0.0
        for counter in counters:
            tot = counter.totalCount()
            for label in counter:
                freq = counter[label]
                if freq != 0:
                    score += freq * math.log(float(freq)/tot, 2)
        return score

    def entropy(self, labels):
        """
        Calculates the entropy value for the given training set
        """
        counter = util.Counter()
        counter.incrementAll(labels, 1)
        return self.entropy_from_counts(counter)

    def entropy_from_counts(self, counter):
        ent = 0.0
        tot = counter.totalCount()
        for c in counter:
            freq = counter[c]
            if freq != 0:
                freq = float(freq)
                ent += (freq/tot) * math.log(freq/tot,2)
        return -1 * ent

    def entropy_x_from_counts(self, counters):
        n = sum(counter.totalCount() for counter in counters)
        entX = 0.0
        for counter in counters:
            entX += float(counter.totalCount()) / n * self.entropy_from_counts(counter)
        return entX

    def max_operator_from_counts(self, counters):
        """Returns the number correct if we split on feature f and then predict
        majority class label.

        Input is a list of counter objects, one for each split value.  Each counter
        object represents a distribution over class labels.
        """
        return sum(counter[counter.argMax()] for counter in counters)

    def gini_index_from_counts(self, counters):
        """Computes gini index.  See Friedman and Schuster, "Data Mining with Differential Privacy", KDD 2010.

        Input is a list of counter objects, one for each split value.  Each counter
        object represents a distribution over class labels.
        """
        score = 0
        for counter in counters:
            tot = counter.totalCount()
            if tot == 0:
                continue
            p = 0
            for label in counter:
                p += (float(counter[label]) / tot) ** 2
            score += tot * (1 - p)
        return -1 * score

    # ---------------------------------------------
    # (END) DISCRETE FEATURE SELECTION FUNCTIONS
    # ---------------------------------------------

    # ---------------------------------------------
    # CONTINUOUS FEATURE SELECTION FUNCTIONS
    # ---------------------------------------------
    def info_gain_continuous(self, data, labels, f):
        return self.find_best_continuous(data, labels, f, self.info_gain_from_counts)

    def max_operator_continuous(self, data, labels, f):
        """Returns the number correct if we split on feature f and then predict
        majority class label.
        """
        return self.find_best_continuous(data, labels, f, self.max_operator_from_counts)

    def gini_index_continuous(self, data, labels, f):
        """Computes gini index.  See Friedman and Schuster, "Data Mining with Differential Privacy", KDD 2010.
        """
        return self.find_best_continuous(data, labels, f, self.gini_index_from_counts)

    def random_split_continuous(self, data, labels, f):
        """Selects a random split and within the max and min range
        randomly select a split
        """
        score = random.random()
        splitPoint = random.randint(self.min, self.max)
        return (score, [[self.min, splitPoint], [splitPoint, self.max]])

    def find_best_continuous(self, trainingData, trainingLabels, f, score_fn):
        """Computes info gain for a continuous attribute by trying all possible
        split points.
        """
        # make (feature value, label) pairs
        # sort by feature value
        # iterate thru value, label pairs and update statistics
        # only measure when adjacent values differ

        # initialize two counters for label distribution to left and right of split point
        left = util.Counter()
        right = util.Counter()
        right.incrementAll(trainingLabels, 1)  # initially all data is to the right of split point

        f_vals, labels = zip(*sorted(self.get_feature_label_pairs(trainingData, trainingLabels, f)))

        best_split = -1
        max_score = score_fn([left, right])

        # note: the left side is all data up to *and including* the feature value at index i
        for i in range(len(f_vals)):
            f_val = f_vals[i]
            label = labels[i]
            # move this label from right to left
            right[label] -= 1
            left[label] += 1
            # if we're at the end of the list or if f_val is distinct from the next f_val,
            # then check to see if we have a new max
            if i == len(f_vals)-1 or f_val != f_vals[i+1]:
                score = score_fn([left, right])
                if score > max_score:
                    best_split = i
                    max_score = score
        if best_split == -1:
            # apparently best split leaves all data to the right!
            # set the feature value as something less than min value
            return (max_score, min(f_vals)-0.0000001)  # todo: add a test case for this
        return (max_score, f_vals[best_split])

    def generateSplitContinuous(self, data, labels, X, splitPoint):
        '''
        given a feature and the splitting point for that feature it divides the data into
        two partitions pivoted at the splitting point
        '''
        data_less = []
        data_greater = []
        labels_less = []
        labels_greater = []

        for (datum, label) in zip(data, labels):
            if datum[X] <= splitPoint:
                data_less.append(datum)
                labels_less.append(label)
            else:
                data_greater.append(datum)
                labels_greater.append(label)
        splitData = [data_less, data_greater]
        splitLabels = [labels_less, labels_greater]
        return (splitData, splitLabels)

    def get_feature_label_pairs(self, trainingData, trainingLabels, f):
        return ((instance[f], label) for instance,label in zip(trainingData,trainingLabels))

    # ---------------------------------------------
    # (END) CONTINUOUS FEATURE SELECTION FUNCTIONS
    # ---------------------------------------------

    # ---------------------------------------------
    # DEBUGGING HELPER FUNCTIONS
    # ---------------------------------------------
    def printDiagnostics(self, depth=None):
        """
        This function is called after the classifier has been trained.  

        It should print the first five levels of the decision tree in a nicely 
        formatted way.  
        """

        self.printHelper(self.root, 0, depth)

    def printHelper(self, node, spacing, depth):
        if depth is not None and depth < 0:
            return
        if not node.isLeaf:
            if hasattr(node, 'splitPoint'):
                splitPoint = " <= " + str(node.splitPoint)
            else:
                splitPoint = ""
            print "   " * spacing + "Split on " + node.splitFeature + splitPoint + ":"
            for s in node.subTrees:
                print "   " * (spacing + 1) + node.splitFeature + " = " + s + " ==>"
                self.printHelper(node.subTrees[s], spacing + 2, depth-1)
        else:
            print "   " * (spacing + 1) + "Label = " + node.label

    # ---------------------------------------------
    # (END) DEBUGGING HELPER FUNCTIONS
    # ---------------------------------------------

    # todo: review the tree pruning code
    # ---------------------------------------------
    # TREE PRUNING CODE
    # ---------------------------------------------
    def prune(self, tree):
        self.topDownCorrect(tree, tree.noisyCount)
        self.bottomUpAggregate(tree)
        self.tree_prune(tree, 0.25)
        return tree

    def topDownCorrect(self, tree, fixedCount):
        '''
        calibrates the total instance count in each level of the tree to match the
        count in the parent level
        '''
        tree.noisyCount = fixedCount
        if not tree.isLeaf:
            subtrees = tree.subTrees
            sumCount = 0
            for val in tree.subTrees.keys():
                sumCount += tree.subTrees[val].noisyCount
            for val in tree.subTrees.keys():
                if sumCount != 0:
                    fixedCountSub = tree.subTrees[val].noisyCount/sumCount*fixedCount
                    self.topDownCorrect(tree.subTrees[val], fixedCountSub)
                else:
                    self.topDownCorrect(tree.subTrees[val], 0)

    def bottomUpAggregate(self, tree):
        '''
        aggregates class counts and calibrates them to match the total instance count
        '''
        if tree.isLeaf:
            sumClassCount = 0
            for label in self.meta.classes:
                sumClassCount += tree.classCount[label]
            for label in self.meta.classes:
                tree.classCount[label]= (tree.classCount[label])*tree.noisyCount/sumClassCount
        else:
            for val in tree.subTrees.keys():
                self.bottomUpAggregate(tree.subTrees[val])
            for label in self.meta.classes:
                sumClassCount = 0
                for val in tree.subTrees.keys():
                    sumClassCount += tree.subTrees[val].classCount[label]
                tree.classCount[label] = sumClassCount

    def tree_prune(self, tree, CF):
        '''
        compares the errors from leaving the tree as it is, changing it to a leaf and raising the subtree
        with the most records to replace the current tree and chooses the option that minimizes the estimated
        error
        '''
        self.getErrorRates(tree, CF)
        if tree.isLeaf:
            return
        T, L, S = tree.errorRates
        if min(T, L, S) == T:
            subtrees = tree.subTrees
            for val in tree.subTrees.keys():
                self.tree_prune(tree.subTrees[val], CF)
        elif min(T, L, S) == L:
            tree.isLeaf = True
            tree.label = findMaxLabel(tree.classCount)
            return
        else:
             tree = self.findMaxSubTree(tree)
             self.tree_prune(tree, CF)

    def getErrorRates(self, tree, CF):
        if tree.isLeaf:
            S = 1000
            error = tree.noisyCount - tree.classCount[tree.label]
            T = (error,tree.noisyCount)
            tree.error = T
            if tree.noisyCount!=0:
                T = Ucf(T,CF)
            else:
                T = 0
            tree.errorRates = (T, T, S)
        else:
            for val in tree.subTrees.keys():
                self.getErrorRates(tree.subTrees[val], CF)
            T = (0,0)

            for val in tree.subTrees.keys():
                x,y = tree.subTrees[val].error
                a,b = T
                T = (x+a, y+b)
            error = tree.noisyCount - tree.classCount[findMaxLabel(tree.classCount)]
            L = (error, tree.noisyCount)
            tree.error = T
            T = Ucf(T, CF)
            L = Ucf(L, CF)
            t = 1
            if not tree.isLeaf:
                t, l, s = self.findMaxSubTree(tree).errorRates
            S = t
            tree.errorRates = (T, L, S)

    def findMaxSubTree(self, tree):
        maxSubTree = None
        maxCount = -1
        for val in tree.subTrees.keys():
            if tree.subTrees[val].noisyCount>maxCount:
                maxCount = tree.subTrees[val].noisyCount
                maxSubTree = tree.subTrees[val]
        return maxSubTree

    # ---------------------------------------------
    # (END) TREE PRUNING CODE
    # ---------------------------------------------
      # ---------------------------------------------
    #  FEATURE SELECTION CODE
    # ---------------------------------------------

    def selectFeatures(self, data, labels, features, n):
        feature_scores = []    
        for f in features:
            if self.meta.is_real(f):                
                assert self.split_real, "Error: self.split_real is False and yet real features are included!"
                (max_score, split) = self.utility_continuous(data, labels, f)                               
                feature_scores.append((max_score,f)) 
            else:
                score = self.utility(data, labels, f)            
                feature_scores.append((score, f))
        return self.get_max_n(feature_scores, n)        
        
    def get_max_n(self, feature_scores, n):
        features = []
        feature_scores = sorted(feature_scores, reverse = True)             
        for item in feature_scores[1:n]:
            score, f = item            
            features.append(f)
        return features



    # ---------------------------------------------
    # (END) FEATURE SELECTION CODE
    # ---------------------------------------------

def Ucf(error, CF):
    M, N  = error
    return beta.ppf(1 - CF, M + 1, N - M)

def findMaxLabel(classCount):
    maxCount = -1
    freqLabel = ''
    for label in classCount.keys():
        if classCount[label]>maxCount:
            maxCount = classCount[label]
            freqLabel = label
    return label

    # ---------------------------------------------
    # (END) TREE PRUNING CODE
    # ---------------------------------------------
