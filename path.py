import ident
import tag
from utils import first, flatten
from cache import instance as CACHE


class Path(object):
    """A wrapper around a tuple of Simple nodes, with some utility methods"""

    IdentCls = ident.Simple

    def __init__(self, nodes, tags=None):
        self.nodes = tuple(nodes)
        tags = tags or [tag.Empty for _ in range(len(nodes))]
        self.tags = tuple(tags)
        assert(len(self.nodes) == len(self.tags))

    def as_list(self):
        """
        >>> path = Path([1, 2, 3], ["TagA", "TagB", "TagC"])
        >>> path.as_list()
        [(1, 'TagA'), (2, 'TagB'), (3, 'TagC')]
        """
        assert(len(self.nodes) == len(self.tags))
        return list(zip(self.nodes, self.tags))

    @classmethod
    def empty(cls):
        """
        >>> Path.empty()
        Path: ()
        """
        return cls(tuple(), tuple())

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

        tags = flatten(
            path.tags
            for path in subpaths)

        return Path(nodes, tags)

    def __eq__(self, other):
        """
        >>> Path([1, 2]) == Path([1, 2])
        True
        >>> Path([1, 2]) == Path([1, 2, 3])
        False
        """
        return type(self) == type(other) and (self.nodes, self.tags) == (other.nodes, other.tags)

    def slice(self, i, j):
        """
        >>> path = Path([1,2,3])
        >>> path.slice(1, 3)
        Path: (2, 3)
        """
        assert(i <= self.length())
        assert(j <= self.length())
        assert(i <= j)
        return Path(
            self.nodes[i:j],
            self.tags[i:j])

    def __add__(self, other):
        return self.concat(other)

    def concat(self, tail):
        """
        >>> Path([1, 2]).concat(Path([3, 4]))
        Path: (1, 2, 3, 4)
        """
        return Path(
            self.nodes + tail.nodes,
            self.tags + tail.tags)

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
        return hash((self.nodes, self.tags))

    def append(self, element, elemTag=None):
        """
        >>> Path([1, 2]).append(3)
        Path: (1, 2, 3)
        """
        elemTag = elemTag or tag.Empty
        return Path(
            self.nodes + (element, ),
            self.tags + (elemTag, ))

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

    def append_tag(self, tag):
        """
        >>> path = Path([1], [tag.Empty])
        >>> path.append_tag(tag.And) == Path([1], [tag.And])
        True
        >>> path = Path([1, 2], [tag.Empty, tag.Empty])
        >>> path.append_tag(tag.Or) == Path([1, 2], [tag.Empty, tag.Or])
        True
        """
        if self.length() is 0:
            return self

        new_tags = self.tags[:-1] + (self.tags[-1].add(tag), )
        return Path(
            self.nodes,
            new_tags)
