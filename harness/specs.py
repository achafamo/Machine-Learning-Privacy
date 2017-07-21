import inspect

__author__ = 'mhay@colgate.edu'


class Spec(object):
    """
    A Spec is a specification of a parameter.
    """

    def getKey(self):
        """Return unique key for this spec."""
        raise Exception("Not yet implemented")

    def resolve(self):
        """Return python object defined by this spec."""
        raise Exception("Not yet implemented")

    def getArgs(self):
        """Return a description of spec"""
        raise Exception("Not yet implemented")


class PrimitiveSpec(Spec):
    """
    A PrimitiveSpec wraps a parameter of primitive type, such as a numerical parameter (e.g., epsilon).
    """
    def __init__(self, obj):
        self.obj = obj

    def getKey(self):
        return self.obj

    def resolve(self):
        return self.obj

    def getArgs(self):
        return {}


class FuncSpec(Spec):
    """
    A FuncSpec wraps a loader function.  It is defined by a python function object f along with its arguments.
    """

    def __init__(self, f, args):
        self.f = f
        self.args = self.completeParams(f, args)

    def completeParams(self, f, args):
        """If specification omits any optional parameters, add them based on
        inspection of function definition spec: (function-ref, argument-dict)
        """
        # get optional parameters and their settings from function definition
        if inspect.getargspec(f).defaults:  # there are some optional params
            optional = dict(zip(reversed(inspect.getargspec(f).args),
                                reversed(inspect.getargspec(f).defaults)))
            for k in optional:    # if an optional param is not in spec, add it
                if k not in args.keys():
                    args[k] = optional[k]
        return args

    def getKey(self):
        """Generates string to use as key from an object spec
        spec: (function-ref, argument-dict)
        """
        argstring = ''
        for k in sorted(self.args.keys()):      # sort to get canonical form
            argstring += ('.' + k  + str(self.args[k]))
        return self.f.__name__ + argstring

    def resolve(self):
        return self.f(**self.args)

    def getArgs(self):
        return self.args


def findSpec(obj):
    """Tries to resolve kind of spec of arbitrary object obj.  Defaults
    PrimitiveSpec.
    """
    if (type(obj) == type((1,)) and len(obj) == 2 and
        hasattr(obj[0], '__call__') and type(obj[1]) == type({})):
        f, arg = obj
        return FuncSpec(f, arg)
    return PrimitiveSpec(obj)