import random
from classifiers.decision_tree import DecisionTree, SPLIT_INFO_GAIN, SPLIT_MAX, SPLIT_GINI
from diffp import noisy_count, e_m, compute_unnormalized_scores, normalize, sample
import math
import diffp
import util

# todo: add support for continuous features: both Friedman's way and improved were first pick feature then split

STOP_FRIEDMAN = "Friedman KDD 2010 stopping criteria"
STOP_NEW = "proposed stopping criteria"

CONTINUOUS_FRIEDMAN = "Friedman continuous handling method"
CONTINUOUS_NEW = "proposed continuous handling method"

class DecisionTreePrivate(DecisionTree):

    def __init__(self, splitter=SPLIT_MAX, depth=3, to_prune=False, split_real=True, stopper=STOP_FRIEDMAN, select_features = False, continuous = CONTINUOUS_NEW, track_epsilon = False ):
        super(DecisionTreePrivate, self).__init__(splitter, depth, to_prune, split_real, select_features)

        self._epsilon = None
        assert stopper in [STOP_FRIEDMAN, STOP_NEW], "Unrecognized stopping criteria specified: {0}".format(stopper)
        self.stopper = stopper   # decides which stopping criteria to use in isDone method
        self.continuous = continuous
        self.track_epsilon = track_epsilon
        if splitter == SPLIT_INFO_GAIN:
            N = 5000               # todo: hmmmm...  this is not correct
            self.sensitivity = math.log(N + 1, 2) + 1/math.log(2)
            self.utility_continuous = self.score_info_gain_continuous
        elif splitter == SPLIT_MAX:
            self.sensitivity = 1
            self.utility_continuous = self.score_max_continuous
        elif splitter == SPLIT_GINI:
            self.sensitivity = 2
            self.utility_continuous = self.score_gini_continuous
        else:
            raise Exception("Unrecognized splitter specified: {0}".format(splitter))

    @property
    def epsilon(self):
        return self._epsilon

    @epsilon.setter
    def epsilon(self, e):
        self._epsilon = e

    def train(self, X, y, meta=None, epsilon=None):
        num_real = sum(1 for f in meta.features if meta.is_real(f) and self.split_real)
        # when self.split_real is False, then num_real is 0 and this is still the correct epsilon
        if self.continuous == CONTINUOUS_FRIEDMAN:
            self._epsilon = float(epsilon) / ((2 + num_real) * self.depth + 2)  # todo: improve this??
        elif self.continuous == CONTINUOUS_NEW:
            self._epsilon = float(epsilon) / ((3) * self.depth + 2)
        if num_real == 0:
            self._epsilon = float(epsilon)/(2)*self.depth + 2
        super(DecisionTreePrivate, self).train(X, y, meta)

    def isDataEmpty(self, trainingData):
        """Always return False since this base cases never happens when private."""
        return False

    def isDone(self, trainingLabels, depth, features):
        if not features:
            return True
        if depth <= 0:
            return True

        # check to see if there is enough data; must be done privately
        if self.stopper == STOP_FRIEDMAN:
            return not self.enoughData(trainingLabels)
        else:
            assert self.stopper == STOP_NEW
            return self.isDataSame(trainingLabels)

    def enoughData(self, trainingLabels):
        """
        This is the stopping condition that is used in the friedman code. It checks if the noisyCount of
        the training data is larger than the standard deviation of the noise being added
        """

        n = noisy_count(len(trainingLabels), self._epsilon)
        C = len(self.meta.classes)
        feature_cards = [self.meta.get_num_values(f) for f in self.meta.features if not self.meta.is_real(f)]
        t = max([2] + feature_cards)  # in case all features are continuous, then t is at least 2

        if float(n)/(t * C) > math.sqrt(2)/self._epsilon:
            (self.currentNode).noisyCount = n  # todo: not crazy about this...  why needed?
            return True
        else:
            (self.currentNode).noisyCount = 0  # todo: why set to zero?
            return False

    # todo: review this method
    def isDataSame(self, trainingLabels):
        """
        this is our new stopping condition which checks if there are at least two  class labels whose counts are
        greater than the standard deviation of the noise. It simultaneously checks if the remaining records all have
        same class label or if there is not enough data to continue splitting on a feature.
        """
        first = False
        temp = False
        dataSame = True
        node = self.currentNode
        noisyCount = 0
        for label in self.meta.classes:
            noisyCount += noisy_count(trainingLabels.count(label), self._epsilon)
            if noisy_count(trainingLabels.count(label), self._epsilon)>math.sqrt(2)/self._epsilon and not first:
                temp = True
            elif noisy_count(trainingLabels.count(label), self._epsilon)>math.sqrt(2)/self._epsilon and first:
                dataSame = False
            first = temp
        node.noisyCount = 0
        if noisyCount> 0:
            node.noisyCount = noisyCount
        return dataSame

    def findPlurality(self, trainingLabels):
        # in private tree, the output of this function should never be used...
        return None

    def assign_label(self, trainingLabels, depth):
        """
        This method is called to find the plurality label. It is usually called if one of the stopping conditions
        is satisfied. Since we need the class count of each label at the leafs for the error based pruning, we set
        a class count attribute to the currentNode.
        """
        classCount = util.Counter()
        e = self._epsilon
        if self.track_epsilon == True:
            e = self._epsilon*(self.depth - depth)
        for label in self.meta.classes:
            classCount[label] = noisy_count(trainingLabels.count(label), e)
        (self.currentNode).classCount = classCount  # todo: not crazy about this...  why needed?
        return classCount.argMax()

    def findSplitFeature(self, trainingData, trainingLabels, features):
        splits = {}  # save the privately chosen feature splits for later use
        feature_scores = []
        for f in features:
            if self.meta.is_real(f):
                assert self.split_real, "Error: self.split_real is False and yet real features are included!"
                (left, right, scores) = self.utility_continuous(trainingData, trainingLabels, f)
                if self.continuous == CONTINUOUS_FRIEDMAN:
                    priv_scores = self.em_scores(left, right, scores)
                    (i, splitPoint) = self.sample(left, right, priv_scores)
                    splits[f] = splitPoint
                    feature_scores.append(scores[i])  # add the true score for this split point
                elif self.continuous == CONTINUOUS_NEW:
                    score = self.choose_max_score(scores)
                    feature_scores.append(score)
            else:
                score = self.utility(trainingData, trainingLabels, f)
                feature_scores.append(score)

        f = diffp.e_m_scores(features, feature_scores, self.sensitivity, self.epsilon)
        if self.meta.is_real(f):
            if self.continuous == CONTINUOUS_FRIEDMAN:
                f = (f, splits[f])  # take best split point that we privately selected before
            elif self.continuous == CONTINUOUS_NEW:
                (left, right, scores) = self.utility_continuous(trainingData, trainingLabels, f)
                priv_scores = self.em_scores(left, right, scores)
                (i, splitPoint) = self.sample(left, right, priv_scores)
                f = (f, splitPoint)        #
        return f

        ### OLD WAY

        # # the exponential mechanism, e_m, expects (a) a private dataset and (b) a utility function.
        # # the utility function must have two parameters, the dataset and an output element
        # # here, our dataset is broken into 2 things -- trainingData and trainingLabels -- and our self.utility takes in
        # # three parameters: training data, training labels, and a feature
        # # this lambda function simply converts the function signature to be a two parameter function
        # # where the first parameter is the tuple (trainingData, training labels)
        # D = (trainingData, trainingLabels)
        # utility_fn = lambda D, f: self.utility(D[0], D[1], f)
        # return e_m(D, utility_fn, self.sensitivity, features, self._epsilon)

    def score_info_gain_continuous(self, trainingData, trainingLabels, f):
        return self.score_continuous_splits(trainingData, trainingLabels, f, self.info_gain_from_counts)

    def score_max_continuous(self, trainingData, trainingLabels, f):
        return self.score_continuous_splits(trainingData, trainingLabels, f, self.max_operator_from_counts)

    def score_gini_continuous(self, trainingData, trainingLabels, f):
        return self.score_continuous_splits(trainingData, trainingLabels, f, self.gini_index_from_counts)

    def score_continuous_splits(self, trainingData, trainingLabels, f, score_fn):
        """Computes score privately for a continuous attribute by trying all possible
        split points.
        """

        # semantics of continuous feature split:
        # decision tree will have a condition:  feature <= value

        # in private computation, first assume that the domain of f is interval [min_val,max_val]
        # training data gives us feature value, label pairs
        # let x_1, x_2, x_3, ..., x_n denote the *distinct* value of f, in *sorted* order
        # we partition domain into
        # [min_val, x_1), [x_1, x_2), [x_2, x_3), ..., [x_{n-1}, x_n), [x_n, max_val]
        # little counter-intuitive that we don't include the left and not the boundary, but
        # that's because the score *changes* precisely when we include x_i because it moves from
        # the right to the left side of the split

        # initialize two counters for label distribution to left and right of split point
        left = util.Counter()
        right = util.Counter()
        right.incrementAll(trainingLabels, 1)  # initially all data is to the right of split point

        f_vals, labels = zip(*sorted(self.get_feature_label_pairs(trainingData, trainingLabels, f)))
        

        min_val = min(f_vals) - 1  # todo: technically this violates diffp!
        max_val = max(f_vals) + 1

        # initialize the data structures for case when all data is to the right of the split
        left_endpts = [min_val]             # represents *left* boundary of interval, inclusive
        right_endpts = [f_vals[0]]          # represents *right* boundary of interval, exclusive
        scores = [score_fn([left, right])]  # initial score has all data to the right of the split

        # note: the left side is all data up to *and including* the feature value at index i
        for i in range(len(f_vals)):
            f_val = f_vals[i]
            label = labels[i]
            # move this label from right to left
            right[label] -= 1
            left[label] += 1
            # if at end of list
            if i == len(f_vals)-1:
                left_endpts.append(f_val)
                right_endpts.append(max_val)
                scores.append(score_fn([left, right]))
            # if f_val is distinct from the next f_val, then add a break point
            elif f_val != f_vals[i+1]:
                left_endpts.append(f_val)
                right_endpts.append(f_vals[i+1])
                scores.append(score_fn([left, right]))

        return (left_endpts, right_endpts, scores)

    # todo: make this a generic diffp method?
    def em_scores(self, left_endpts, right_endpts, scores):
        assert len(scores) == len(left_endpts) and len(scores) == len(right_endpts)
        scores = compute_unnormalized_scores(scores, self.sensitivity, self.epsilon)
        # scale each score up by the size of the interval it represents
        for i in range(len(scores)):
            scores[i] *= right_endpts[i] - left_endpts[i]
        return normalize(scores)

    def sample(self, left_endpts, right_endpts, scores):
        assert len(scores) == len(left_endpts) and len(scores) == len(right_endpts)
        # sample an interveral with probability proportional to the interval's score
        i = diffp.sample(scores)
        # then sample a split point uniformly at random w/in chosen interval
        f_val = left_endpts[i] + random.random() * (right_endpts[i] - left_endpts[i])
        return (i, f_val)
    # ---------------------------------------------
    #  FEATURE SELECTION CODE
    # ---------------------------------------------
    def selectFeatures(self, data, labels, features, n):
        T = self.get_threshold(data, labels, features, n)         
        return self.PTT(T, data, labels, features)
    def get_threshold(self, data, labels, features, n):
        feature_scores = []
        for f in features:
            if self.meta.is_real(f):                
                assert self.split_real, "Error: self.split_real is False and yet real features are included!"
                (left, right, scores) = self.utility_continuous(data, labels, f)                
                priv_scores = self.em_scores(left, right, scores)
                (i, splitPoint) = self.sample(left, right, priv_scores)               
                feature_scores.append((scores[i],f)) 
            else:
                score = self.utility(data, labels, f)            
                feature_scores.append((score, f))
    
        feature_scores = sorted(feature_scores, reverse = True)        
        T = feature_scores[n]        
        score, f  = T         
        return score 

    def PTT(self, T, data, labels, features):
        '''
        this method preturbs the threshold and thereby making it differentially private  
        '''
        new_features = []        
        T = self.add_laplace_noise(T, self.sensitivity, self._epsilon)              
        for f in features:                      
            if self.meta.is_real(f):
                assert self.split_real, "Error: self.split_real is False and yet real features are included!"
                (left, right, scores) = self.utility_continuous(data, labels, f)                
                priv_scores = self.em_scores(left, right, scores)
                (i, splitPoint) = self.sample(left, right, priv_scores)                 
                score = scores[i]
            else:
                score = self.utility(data, labels, f)              
            if score >T:                
                new_features.append(f)            
        return new_features

    def add_laplace_noise(self, T, sensitivity, epsilon):
        b = sensitivity / epsilon
        u = random.uniform(-0.5, 0.5)          
        return T + (-1 * b * diffp.sgn(u) * math.log(1 - 2 * math.fabs(u)))

    # ---------------------------------------------
    # (END) FEATURE SELECTION CODE
    # ---------------------------------------------

    # ---------------------------------------------
    # NEW CONTINUOUS ATTRIBUTE FEATURE
    # ---------------------------------------------

    def choose_max_score(self, scores):
        return max(scores)
                




    # ---------------------------------------------
    # (END) NEW CONTINUOUS ATTRIBUTE FEATURE
    # ---------------------------------------------