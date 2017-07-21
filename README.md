# pclass

This repo holds our code for different private classification algorithms.
The name, pclass, is short for private classification.

## Directory structure



- `data` holds (small) `.arff` files
- `classifier` holds all classifiers, both non-private and private.  if a particular classifier
  requires additional support code (e.g., GUPT) that should live in an appropriately named subdirectory

- `diffp.py` holds generic privacy algorithms such as the exponential mechanism
- `util.py` holds generic utilities like a Counter class

## Unit tests

Each folder should have a `test` subdirectory with unit tests.  The unit test
file should be named `test_x.py` where `x` is the name of the module that it tests.
See, for example, `classifiers.test.test_onerule.py`.