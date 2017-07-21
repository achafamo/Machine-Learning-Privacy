import os
import random
import re
import sys


def readlines(filename):
    if not os.path.exists(filename):
        this_dir = os.path.dirname(sys.modules[__name__].__file__)  # hack to find this directory
        #todo: make data directory location configurable
        filename = os.path.join(this_dir, os.path.basename(filename))
    if os.path.exists(filename):
        return [l.rstrip() for l in open(filename).readlines()]
    else:
        assert False, 'Cannot find file with name {0}'.format(filename)

def split(X, y, n=None):
    '''Split dataset X and labels y into train/test split.  Parameter n
    (if supplied) is the size of the training set, with remainder going
    to test set.  if n is omitted, it does 50%/50% train/test split.
    '''

    pairs = zip(X, y)
    random.shuffle(pairs)
    X, y = zip(*pairs)
    if n is None:
        n = len(X) / 2
    trainX = X[:n]
    trainY = y[:n]
    testX = X[n:]
    testY = y[n:]
    return (trainX, trainY, testX, testY)

class MetaData(object):

    def __init__(self, feature_dict, classes):
        self._features = dict(feature_dict)
        self._classes = classes

    @property
    def features(self):
        return sorted(self._features.keys())

    @features.setter
    def features(self, f):
        raise Exception("Not allowed to modify features!")

    def is_real(self, f):
        assert f in self._features
        return self._features[f] == 'real'

    def get_values(self, f):
        assert not self.is_real(f)
        return self._features[f]

    def get_num_values(self, f):
        return len(self.get_values(f))

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, f):
        raise Exception("Not allowed to modify classes!")


def load_data_from_string(s):
    return _load(s.split('\n'))

def load_data(filename, n=None):
    return _load(readlines(filename), n)

def _load(lines, n=None):
    """
    Loads data in a file that meets the Weka ARFF format.
    http://www.cs.waikato.ac.nz/ml/weka/arff.html
    """
    processing_data = False
    attributes = []
    data = []
    labels = []
    missing_value = False
    for line in lines:
        line = line.lower()
        if line.startswith('%') or line.strip() == '':
            continue
        elif line.startswith('@attribute'):
            assert not processing_data
            matchObj = re.search(r"@attribute ([\S]+)\s+\{\s*(.*\S)\s*\}", line)
            if matchObj is None:
                matchObj = re.search(r"@attribute ([\S]+)\s+(real|numeric)", line)
            if matchObj is None:
                print "Can't parse this line", line
                assert matchObj is not None
            attr, legal_values = matchObj.groups()
            if legal_values == 'numeric' or legal_values == 'real':
                legal_values = 'real'
            else:
                legal_values = re.split(r'\s*,\s*', legal_values)
            attributes.append((attr, legal_values))
        elif line.startswith('@data'):
            processing_data = True
            label, legal_labels = attributes[-1]
        elif processing_data:
            values = re.split(r'\s*,\s*', line)            
            assert len(values) == len(attributes), str(values) + str(attributes)
            datum = {}
            for i in range(len(attributes) - 1):
                attr = attributes[i][0]
                legal_values = attributes[i][1]
                if legal_values == 'real':
                    datum[attr] = float(values[i])
                else:
                    #assert values[i] in legal_values, values[i] + str(legal_values)
                    if values[i] == '?':
                        missing_value = True
                    datum[attr] = values[i]
            if not missing_value:
                data.append(datum)
            missing_value = False
            labels.append(values[-1])
    if n is None:
        n = len(data)
    if len(data) < n:
        print "Truncating at %d examples (maximum)" % len(data)

    return data[:n], labels[:n], MetaData(attributes[:-1], legal_labels)
