import json

from path import Path
from utils import first, flatten, selections, dumps


class Node(object):
    def dumps(self):
        return dumps(self)
        return json.dumps(
            self,
            indent = 4,
            default = lambda n: n.to_json() if hasattr(n, "to_json") else n)

    def __hash__(self):
        return hash(self.id())

    def __eq__(self, other):
        return type(self) is type(other) and self.id() == other.id()


class Simple(Node):

    def __init__(self, name, dependency=None):
        self.name = name
        self.dependency = dependency or Nil

    def id(self):
        return self.name

    def __repr__(self):
        return self.id()

    def to_json(self):
        return {
            "id": self.id(),
            "dep": self.dependency }

    def paths(self, prefix):
        """ Get all possible paths from self to Nil.
        FIXME: check for circular lists

        >>> A = Simple("A")
        >>> list(A.paths(Path.empty()))
        [Path: (A,)]

        >>> B = Simple("B", A)
        >>> list(B.paths(Path.empty()))
        [Path: (B, A)]

        >>> list(B.paths(Path([A])))  # A present in prefix and dependencies
        []
        """
        return (
            path
            for path in self.dependency.paths(
                prefix.append(self))
            if path.solvable())


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
        """
        >>> A = Simple("A")
        >>> B = Simple("B")
        >>> node = And([A, B])
        >>> list(node.paths(Path.empty()))
        [Path: (A, B)]

        >>> list(node.paths(Path([A])))  # A present in prefix
        []
        """
        def megapath(prefix, suffixes):
            elements = [prefix] + [
                suffix - prefix
                for suffix in suffixes]

            return Path.chain(elements)

        subpaths_per_child = [
            (
                subpath
                for subpath in child.paths(prefix)
                if subpath.solvable())
            for child in self.children]

        megapaths = (
            megapath(prefix, selection)
            for selection in selections(subpaths_per_child))

        return (
            megapath
            for megapath in megapaths
            if megapath.solvable())


class Or(Complex):
    @staticmethod
    def operator():
        return " + "

    def paths(self, prefix):
        """
        >>> A, B, C = [Simple(x) for x in ("A", "B", "C")]
        >>> node = Or([B, C])
        >>> list(node.paths(Path([A])))
        [Path: (A, B), Path: (A, C)]

        >>> list(node.paths(Path([A, B])))  # B would cause a conflict, C is fine
        [Path: (A, B, C)]
        """
        return (
            subpath
            for child in self.children
            for subpath in child.paths(prefix)
            if subpath.solvable())


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
