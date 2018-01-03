from rosol import ident
from rosol.utils import first, flatten
from rosol.cache import instance as CACHE


class Path(object):
    """A wrapper around a tuple of Simple nodes, with some utility methods"""

    IdentCls = ident.Simple

    def __init__(self, nodes):
        self.nodes = tuple(nodes)

    @classmethod
    def empty(cls):
        """
        >>> Path.empty()
        Path: ()
        """
        return cls(tuple())

    @classmethod
    def chain(cls, subpaths):
        """
        >>> subpaths = [Path([1, 2]), Path([3]), Path([4])] 
        >>> Path.chain(subpaths)
        Path: (1, 2, 3, 4)
        """
        nodes = flatten(
            path.nodes
            for path in subpaths)

        return Path(nodes)

    def __eq__(self, other):
        """
        >>> Path([1, 2]) == Path([1, 2])
        True
        >>> Path([1, 2]) == Path([1, 2, 3])
        False
        """
        return type(self) == type(other) and self.nodes == other.nodes

    def slice(self, i, j):
        """
        >>> path = Path([1,2,3])
        >>> path.slice(1, 3)
        Path: (2, 3)
        """
        assert(i <= self.length())
        assert(j <= self.length())
        assert(i <= j)
        return Path(self.nodes[i:j])

    def __add__(self, other):
        return self.concat(other)

    def concat(self, tail):
        """
        >>> Path([1, 2]).concat(Path([3, 4]))
        Path: (1, 2, 3, 4)
        """
        return Path(self.nodes + tail.nodes)

    def suffix(self, prefix):
        """
        >>> Path([1, 2, 3, 4]).suffix(Path([1, 2]))
        Path: (3, 4)
        """
        assert(self.length() >= prefix.length())
        cutoff = prefix.length()
        assert(self.nodes[ : cutoff] == prefix.nodes)
        return self.slice(cutoff, self.length())

    def __sub__(self, other):
        return self.suffix(other)

    def __repr__(self):
        return "Path: {}".format(self.nodes)

    def __hash__(self):
        return hash(self.nodes)

    def append(self, element):
        """
        >>> Path([1, 2]).append(3)
        Path: (1, 2, 3)
        """
        return Path(
            self.nodes + (element, ))

    def solvable(self):
        cached = CACHE.get(self.nodes)
        if cached:
            return cached
        else:
            return not self.IdentCls.are_conflicting(self._idents())

    def _idents(self):
        return [
            node.ident
            for node in self.nodes]

    def length(self):
        return len(self.nodes)

    def has(self, node):
        return node in self.nodes

