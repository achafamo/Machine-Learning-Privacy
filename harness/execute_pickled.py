
import pickle
import sys

pickle_out = True

if __name__ == '__main__':
    infilename = sys.argv[1]
    outfilename = sys.argv[2]
    idx = int(sys.argv[3]) 

    L = pickle.load(open(infilename))[idx]
    f = L[0]
    args = L[1:]
    out = f(*args)
    print out
    if pickle_out:
        pickle.dump(out, open(outfilename, 'w'))

