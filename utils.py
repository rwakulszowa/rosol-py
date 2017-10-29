from itertools import chain


def flatten(nested):
    assert(len(nested) > 0)
    constructor = type(nested[0])
    return constructor(chain(*nested))

def trace(foo):
    def inner(*args, **kwargs):
        print("-> {}, {}".format(args, kwargs))
        ans = foo(*args, **kwargs)
        print("<- {}".format(ans))
        return ans
    return inner

def first(it, test):
    return next(
        el for el in it if test(el))

