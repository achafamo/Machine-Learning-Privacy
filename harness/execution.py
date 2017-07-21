import itertools
import os
import pandas as pd
import time
import sys

from harness.data_store import DataStore
from harness.specs import findSpec
import pbs_util
from util import get_full_path

RUNTIME = 'e_runtime'

class ExperimentLauncher(object):

    def __init__(self, name, experiment_fn, args, arg_spaces, run_local=True):
        """
        ExperimentLauncher is the configuration for an experiment
        :param name: name of the experiment
        :param experiment_fn: a function object corresponding to the code that will execute experiment
        :param args: ordered list of names of arguments to experiment_fn
        :param arg_spaces: dict where key is name of arg, value is a a list of values arg can take
        :param run_local: if True, runs on local machine, if False, launches on cluster
        :return:
        """
        self.name = name
        self.experiment_fn = experiment_fn
        self.args = args
        self.arg_spaces = arg_spaces
        assert set(self.arg_spaces.keys()) == set(self.args)
        self.run_local = run_local
        self.reset = False

    def clear_results(self):
        """If this experiment has been run before, then override old results.
        """
        self.reset = True

    def launch(self):
        """
        Runs self.experiment_fcn on every possible combination of self.args from self.arg_spaces

        Results are stored in data store using self.name
        """
        arg_spaces_list = []
        for arg in self.args:
            arg_values = self.arg_spaces[arg]
            arg_values = map(findSpec, arg_values)   # convert each to a specification
            arg_spaces_list.append(arg_values)

        schema = self.args  # must match args of experimentFn
        data_store_dir = get_full_path('experiments', 'store') #os.path.join('store', self.name)
        assert os.path.exists(data_store_dir)
        dstore = DataStore(data_store_dir, self.name, schema, self.reset)

        configurations = crossProduct(*arg_spaces_list)

        filtered = filterConfigurations(configurations, dstore)

        if self.run_local:
            executeBatch(self.experiment_fn, filtered, schema, dstore)
        else:
            executeBatchPBS(self.experiment_fn, filtered, schema, dstore)

        df = dstore.retrieve([map(lambda x: x.getKey(), config) for config in configurations])

        summarize(df, schema)

        return df

def crossProduct(*iterables):
    return list(itertools.product(*iterables))

def filterConfigurations(configurations, dstore):
    if dstore == None:
        return configurations
    else:
        configurations2 = []
        origTotal = len(configurations)
        # convert specs to keys
        configKeys = [ tuple(map(lambda x: x.getKey(), config)) for config in configurations]

        for i in range(len(configKeys)):
            if dstore.getCount(configKeys[i]) == 0:
                configurations2.append(configurations[i])

        print '%i of %i executions remain after filtering' % (len(configurations2), origTotal)
    return configurations2

def executeBatch(f, configurations, schema, dstore=None, startSeed=None, updateStore=True):
    if not configurations:  #useful case to catch in case filtering resulted in empty paramTuples
        return None

    if dstore == None:
        dstore = DataStore()      # create new empty datastore (note: can't be saved)
        updateStore = False

    df = pd.DataFrame(columns=schema)

    for config in configurations:
        keys = map(lambda x: x.getKey(), config)
        args = map(lambda x: x.resolve(), config)

        start = time.time()
        results = f(*args)
        elapsed = time.time() - start

        # add in columns for the specs, as needed
        extra = {}
        for c in config: 
            extra.update(c.getArgs())
        config = dict(zip(schema, keys))  
        config[RUNTIME] = elapsed
        config.update(extra)
        config_df = pd.DataFrame([config])
        results_df = pd.DataFrame(results)
        # duplicate rows of config_df to match size of results_df
        config_df = pd.concat( [config_df] * len(results_df), ignore_index=True)
        results = pd.concat( [config_df, results_df], axis=1)
        df = df.append(results, ignore_index=True)

    if updateStore:
        dstore.addExp(df)
        dstore.save()

    return df

def executeBatchPBS(f, configurations, schema, dstore=None, startSeed=None, updateStore=True):
    if not configurations:  #useful case to catch in case filtering resulted in empty paramTuples
        return None

    if dstore == None:
        dstore = DataStore()      # create new empty datastore (note: can't be saved)
        updateStore = False

    batch = []
    for config in configurations:
        batch.append((wrapperFunction,f) + config)

    pbs = pbs_util.PBS(batch)
    pbs.qsub()
    count = pbs.unfinished()
    while count > 0:
        print count, 'remaining tasks'
        time.sleep(5)
        count = pbs.unfinished()
    results_batch = pbs.retrieve()
    pbs.cleanup()

    if len(results_batch) != len(configurations):
        print >>sys.stderr, "Error executing on server, check logs on server!"

    df = pd.DataFrame(columns=schema)

    for i in range(len(results_batch)):
        config = configurations[i]
        keys = map(lambda x: x.getKey(), config)
        results = results_batch[i]
        elapsed = results['elapsed']
        results = results['output']

        # add in columns for the specs, as needed
        extra = {}
        for c in config: 
            extra.update(c.getArgs())
        config = dict(zip(schema, keys))  
        config[RUNTIME] = elapsed
        config.update(extra)
        config_df = pd.DataFrame([config])
        results_df = pd.DataFrame(results)
        # duplicate rows of config_df to match size of results_df
        config_df = pd.concat( [config_df] * len(results_df), ignore_index=True)
        results = pd.concat( [config_df, results_df], axis=1)
        df = df.append(results, ignore_index=True)

    if updateStore:
        dstore.addExp(df)
        dstore.save()

    return df

def wrapperFunction(*args):
    """Wraps the main experiment function for running remotely on cluster, see executeBatchPBS.
    """
    f = args[0]
    args = map(lambda x: x.resolve(), args[1:])  # assumes remaining are specifications

    start = time.time()
    results = f(*args)
    elapsed = time.time() - start

    return {'elapsed': elapsed, 'output': results}

def summarize(exp_df, schema):
    if len(exp_df) > 0:
        print 'Number of executions: %i' % exp_df.count(0)[RUNTIME]  # any attribute here
        print 'Total computation time: %f' % exp_df.sum(0)[RUNTIME]
        for colName in schema:
            print 'Distinct %s:' % colName, list(set( exp_df[colName].tolist() ))
    else:
        print >>sys.stderr, "Data frame is empty!"
