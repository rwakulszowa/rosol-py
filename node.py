import json

from utils import first, flatten


class Node(object):
    def dumps(self):
        return json.dumps(
            self,
            indent = 4,
            default = lambda n: n.to_json() if hasattr(n, "to_json") else n)


class Simple(Node):

    def __init__(self, name, dependency):
        self.name = name
        self.dependency = dependency

    def id(self):
        return self.name

    def __repr__(self):
        return "{}: {}".format(
            self.id(),
            self.dependency.id())

    def to_json(self):
        return {
            "id": self.id(),
            "dep": self.dependency }

    def paths(self, acc):
        """ Get all possible paths from self to Nil.
        FIXME: generators, check for circular lists
        """
        return self.dependency.paths([
            prefix + (self.name, )
            for prefix in acc])

    def resolve(self, prefix):
        return self.dependency.resolve(
            prefix + (self, ))


class Complex(Node):
    def __init__(self, children):
        self.children = children

    def id(self):
        inner = self.operator().join(
            child.id()
            for child in self.children)

        return "({})".format(inner)

    def __repr__(self):
        return self.id()

    def to_json(self):
        return {
            "id": self.id(),
            "dep": self.children }

    def paths(self, acc):
        #TODO: move to `And` and `Or`; And should return a megapath, or should return multiple options; all of them should be generators
        updated = [
            prefix + (self, )
            for prefix in acc]

        return flatten([
            child.paths(updated)
            for child in self.children])


class And(Complex):
    @staticmethod
    def operator():
        return " * "

    def resolve(self, acc):

        def _unsolvable(subpaths):
            return any(
                path is None
                for path in subpaths)

        def _get_suffix(total, prefix):
            assert(
                total[ : len(prefix)] == prefix)
            return total[len(prefix) : ]

        sub = [
            child.resolve(acc)
            for child in self.children]

        if _unsolvable(sub):
            return None
        else:
            suffixes = [
                _get_suffix(subpath, acc)
                for subpath in sub]

            #NOTE: it is probably guaranteed that suffixes don't contain `And` nodes
            #NOTE: this method should probably return a list/set of nodes (packages? ids? something with all the dependency crap stripped) in all cases
            #NOTE: acc should also probably be a list of simple nodes (a `Path`)
            #NOTE: basically, all caching / conflict resolution checking is done on a Path of simple nodes, but all weird special cases are handled inside nodes (i.e. Or with multiple options and And with a megapath)
            #NOTE: this should actually reuse the `paths` method: if an `And` node fails, it should try all other possible subpaths (coming from `Or` nodes)
            megapath = acc + flatten(suffixes)
            #FIXME: this is actually wrong:
            #TODO: conflict checking (`Path`)
            #TODO: try all possible subpaths (`paths`)
            return megapath



class Or(Complex):
    @staticmethod
    def operator():
        return " + "

    def resolve(self, acc):
        return first(
            (
                child.resolve(acc)
                for child in self.children),
            lambda n: n is not None)


class Nil(Node):
    @staticmethod
    def id():
        return "()"

    @staticmethod
    def to_json():
        return None

    @staticmethod
    def paths(acc):
        return acc

    @staticmethod
    def resolve(prefix):
        return prefix
