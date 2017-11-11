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

    def paths(self, prefix):
        """ Get all possible paths from self to Nil.

        Filters out unsolvable paths, doesn't hang on circular dependencies.

        >>> A = Simple("A")
        >>> list(A.paths(Path.empty()))
        [Path: (A,)]

        >>> B = Simple("B", A)
        >>> list(B.paths(Path.empty()))
        [Path: (B, A)]

        >>> list(B.paths(Path([A])))  # A present in prefix and dependencies (this test depends on `Path`'s current behavior
        []

        >>> C = Simple("C")
        >>> node = And([A, C])
        >>> list(node.paths(Path.empty()))
        [Path: (A, C)]

        >>> list(node.paths(Path([A])))  # A present in prefix
        []

        >>> D = Simple("D")
        >>> node = Or([C, D])
        >>> list(node.paths(Path([A])))
        [Path: (A, C), Path: (A, D)]

        >>> list(node.paths(Path([A, C])))  # C would cause a conflict, D is fine
        [Path: (A, C, D)]
        """
        #TODO: check if prefix is solvable (if it makes sense)
        return (
            path
            for path in self._subpaths(prefix)
            if path.solvable())

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

    def _subpaths(self, prefix):
        """
        Get `self.children`'s subpaths, break on circular dependency

        This method doesn't filter out unsolvable paths -> it shouldn't
        be directly called by any method other than `self.paths`
        >>> A = Simple("A")
        >>> list(A._subpaths(Path.empty()))
        [Path: (A,)]

        >>> B = Simple("B")
        >>> list(B._subpaths(Path([A])))
        [Path: (A, B)]
        """
        circular = prefix.has(self)
        new_prefix = prefix.append(self)

        return self.dependency.paths(new_prefix) if not circular else [new_prefix]


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

    def _subpaths(self, prefix):
        """
        >>> A = Simple("A")
        >>> B = Simple("B")
        >>> C = And([A, B])
        >>> list(C._subpaths(Path.empty()))
        [Path: (A, B)]

        >>> D = Simple("D")
        >>> list(C._subpaths(Path([D])))
        [Path: (D, A, B)]

        """
        def megapath(prefix, suffixes):
            elements = [prefix] + [
                suffix - prefix
                for suffix in suffixes]

            return Path.chain(elements)

        subpaths_per_child = [
            child.paths(prefix)
            for child in self.children]

        return (
            megapath(prefix, selection)
            for selection in selections(subpaths_per_child))


class Or(Complex):
    @staticmethod
    def operator():
        return " + "

    def _subpaths(self, prefix):
        """
        >>> A = Simple("A")
        >>> B = Simple("B")
        >>> C = Or([A, B])
        >>> list(C._subpaths(Path.empty()))
        [Path: (A,), Path: (B,)]

        >>> D = Simple("D")
        >>> list(C._subpaths(Path([D])))
        [Path: (D, A), Path: (D, B)]
        """
        return (
            subpath
            for child in self.children
            for subpath in child.paths(prefix))



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
