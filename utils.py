import itertools

def flatten(nested):
    return itertools.chain(*nested)

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

def selections(sources):
    """
    >>> selections([])
    [[]]

    >>> selections([[1]])
    [[1]]

    >>> selections([[1, 2], [3, 4]])
    [[1, 3], [1, 4], [2, 3], [2, 4]]
    """
    #FIXME: generators
    if len(sources) is 0:
        return [[]]
    else:
        head, tail = sources[0], sources[1:]
        subresults = selections(tail)
        return [
            [head_element] + subresult
            for head_element in head
            for subresult in subresults]

if __name__ == "__main__":
    import doctest
    doctest.testmod()

