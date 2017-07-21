import pandas as pd
import os

class DataStore:
    """ Data storage methods for persistent experiments """

    def __init__(self, dataDir=None, filePrefix=None, schema=None, reset=False):   # e.g. fileRoot = /path/fileRoot
        """ initialize with file
            if fileRoot is None, use datastore as temporary cache.  Save() will not work
        """
        if dataDir is not None and filePrefix is not None:
            assert os.path.exists(dataDir)
            self.fileRoot = os.path.join(dataDir, filePrefix)
        else:
            self.fileRoot = None
        if reset and os.path.exists(self.fileRoot + '.expf.msg'):
            os.remove(self.fileRoot + '.expf.msg')
            assert not os.path.exists(self.fileRoot + '.expf.msg')

        self.schema = schema
        self.grouped = None
        if (self.fileRoot is None) or (not os.path.exists(self.fileRoot + '.expf.msg')):
            self.expf = pd.DataFrame(columns=schema)            
        else:   # will recover stored versions lazily
            self.expf = None

    def _expf(self):
        if self.expf is None:
            self.expf = pd.read_msgpack(self.fileRoot + '.expf.msg')
        return self.expf

    def _grouped(self):
        if self.grouped is None:
            self.grouped = self._expf().groupby(self.schema).size()
        return self.grouped

    def getCount(self, keyTuple):
        assert len(keyTuple) == len(self.schema)
        if not self._grouped().empty:
            return self._grouped().get(keyTuple, 0)   # returns matching count, or zero if no match
        else:
            return 0

    def addExp(self, newexp):
        """ Add dataframe with newly-computed experimental results"""
        # concatenate results 
        self.expf = pd.concat([newexp, self._expf() ]) # union
        self.expf = self._expf().reset_index(drop=True)
        self.grouped = None # reset because it will need to be recomputed if needed

    def retrieve(self, configKeys=None):
        if configKeys is None:
            expDF = self._expf()    # all stored results
        else:
            filter = pd.DataFrame(configKeys, columns=self.schema)
            expDF = pd.merge(filter, self._expf(), on=self.schema)

        return expDF

    def save(self):     
        if self.fileRoot:
            pd.to_msgpack(self.fileRoot + '.expf.msg', self.expf)
        else: 
            print 'DataStore not saved.'
