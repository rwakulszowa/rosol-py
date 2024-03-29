import itertools
import json


def flatten(nested):
    """
    >>> list(flatten([]))
    []
    >>> list(flatten([ [1, 2], [3, 4] ]))
    [1, 2, 3, 4]
    """
    return itertools.chain(*nested)

def trace(foo):
    def inner(*args, **kwargs):
        print("-> {}, {}".format(args, kwargs))
        ans = foo(*args, **kwargs)
        print("<- {}".format(ans))
        return ans
    return inner

def first(it):
    """
    >>> first(
    ...    x
    ...    for x in [1,2,3]
    ...    if x % 2 is 0)
    2
    """
    try:
        return next(it)
    except StopIteration:
        return None


def selections(sources):
    """
    >>> selections([])
    [[]]

    >>> selections([[1]])
    [[1]]

    >>> selections([[1, 2], [3, 4]])
    [[1, 3], [1, 4], [2, 3], [2, 4]]

    >>> selections([[1], []])
    [[]]
    """
    #FIXME: generators
    if len(sources) is 0:
        return [[]]
    if any(len(sub) is 0 for sub in sources):
        return [[]]
    else:
        head, tail = sources[0], sources[1:]
        subresults = selections(tail)
        return [
            [head_element] + subresult
            for head_element in head
            for subresult in subresults]

def dumps(obj):
    return json.dumps(
        obj,
        indent = 4,
        default = lambda n: n.to_json() if hasattr(n, "to_json") else n.__dict__)


def make_gen(value):
    """
    >>> next(make_gen("xaxa"))
    'xaxa'
    """
    #FIXME: there must be a better way to do this
    yield value


def split(seq, key):
    positive = (el for el in seq if key(el))
    negative = (el for el in seq if not key(el))
    return positive, negative
