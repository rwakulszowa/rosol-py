import json

import ident
from path import Path
import tag
from utils import first, flatten, selections, dumps, make_gen


class Dependency(object):
    def __init__(self, data_gen):
        self.data_gen = data_gen
        self._cached = None

    def resolve(self):
        if not self._cached:
            self._cached = next(self.data_gen)
        return self._cached

    @classmethod
    def make(cls, node):
        return Dependency(
            make_gen(node))

    @staticmethod
    def tag():
        return tag.AndOr


class NilDependency(Dependency):

    @staticmethod
    def resolve():
        return Nil

    @staticmethod
    def tag():
        return tag.Empty


class Node(object):
    PathCls = Path
    IdentCls = ident.Simple

    def dumps(self):
        return dumps(self)

    def paths(self, prefix=None, trailing_tag=None):
        """ Get all possible paths from self to Nil.

        Filters out unsolvable paths, doesn't hang on circular dependencies.

        >>> A = Simple("A")
        >>> list(A.paths())
        [Path: (A,)]

        >>> B = Simple("B", Dependency.make(A))
        >>> list(B.paths())
        [Path: (B, A)]

        >>> list(B.paths(Path([A])))  # A present in prefix and dependencies
        []

        >>> C = Simple("C")
        >>> node = And([A, C])
        >>> list(node.paths())
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
        prefix = prefix or self.PathCls.empty()

        return (
            path
            for path in self._subpaths(prefix, trailing_tag)
            if path.solvable())

    def __hash__(self):
        return hash(self.id())

    def __eq__(self, other):
        return type(self) is type(other) and self.id() == other.id()


class Simple(Node):

    def __init__(self, id, dependency=None):
        self.ident = id if isinstance(id, self.IdentCls) else self.IdentCls(id)
        self.dependency = dependency or NilDependency

    def id(self):
        return str(self.ident)

    def __repr__(self):
        return self.id()

    def to_json(self):
        return {
            "id": self.id(),
            "dep": self.dependency }

    def _subpaths(self, prefix, trailing_tag=None):
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
        new_prefix = prefix.append(
            self,
            trailing_tag or tag.Empty)
        new_trailing_tag = self.dependency.tag()
        #TODO: check if new_prefix is solvable

        if circular:
            return [new_prefix]
        else:
            return self.dependency.resolve().paths(new_prefix, new_trailing_tag)


class Complex(Node):
    def __init__(self, children):
        # Convert to a tuple in case it was passed an iterator
        self.children = tuple(children)

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

    def _subpaths(self, prefix, trailing_tag=None):
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
            child.paths(prefix, trailing_tag)
            for child in self.children]

        return (
            megapath(prefix, selection)
            for selection in selections(subpaths_per_child))


class Or(Complex):
    @staticmethod
    def operator():
        return " + "

    def _subpaths(self, prefix, trailing_tag=None):
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
            for subpath in child.paths(prefix, trailing_tag))


class Nil(Node):
    @staticmethod
    def id():
        return "()"

    @staticmethod
    def to_json():
        return None

    @staticmethod
    def paths(prefix, trailing_tag=None):
        yield prefix
