import json

from path import Path
from utils import first, flatten


class Node(object):
    def dumps(self):
        return json.dumps(
            self,
            indent = 4,
            default = lambda n: n.to_json() if hasattr(n, "to_json") else n)

    def __hash__(self):
        return hash(self.id())

    def __eq__(self, other):
        return type(self) is type(other) and self.id() == other.id()


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

    def paths(self, prefix):
        """ Get all possible paths from self to Nil.
        FIXME: check for circular lists
        """
        return self.dependency.paths(
            prefix.append(self))

    def resolve(self, prefix):  #FIXME
        return self.dependency.resolve(
            prefix.append(self))


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


class And(Complex):
    @staticmethod
    def operator():
        return " * "

    def paths(self, prefix):
        raise NotImplementedError  #FIXME

    def resolve(self, acc):

        def _unsolvable(subpaths):  #FIXME: this is just wrong; do the check on Path, don't return None (return an empty generator instead / filter by solvable)
            return any(
                path is None
                for path in subpaths)

        def _get_suffix(total, prefix):
            return total.suffix(prefix)

        sub = [
            child.resolve(acc)
            for child in self.children]

        if _unsolvable(sub):
            return None
        else:
            suffixes = [
                _get_suffix(subpath, acc)
                for subpath in sub]

            megapath = acc + flatten(suffixes)
            return megapath



class Or(Complex):
    @staticmethod
    def operator():
        return " + "

    def paths(self, prefix):
        return (
            subpath
            for child in self.children
            for subpath in child.paths(prefix))

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
    def paths(prefix):
        yield prefix

    @staticmethod
    def resolve(prefix):
        return prefix
