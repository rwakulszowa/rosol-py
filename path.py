from utils import flatten


class Path(object):
    """A wrapper around a tuple of Simple nodes, with some utility methods"""
    def __init__(self, nodes):
        self.nodes = tuple(nodes)

    @classmethod
    def empty(cls):
        return cls(tuple())

    @classmethod
    def chain(cls, subpaths):
        nodes = flatten(
            path.nodes
            for path in subpaths)

        return Path(nodes)

    def __eq__(self, other):
        return type(self) == type(other) and self.nodes == other.nodes

    def __add__(self, other):
        return self.concat(other)

    def concat(self, tail):
        return Path(self.nodes + tail.nodes)

    def suffix(self, prefix):
        assert(self.length() >= prefix.length())
        cutoff = prefix.length()
        assert(self.nodes[ : cutoff] == prefix.nodes)
        return Path(self.nodes[cutoff : ]) 

    def __sub__(self, other):
        return self.suffix(other)

    def __repr__(self):
        return "Path: " + " -> ".join(
            node.id()
            for node in self.nodes)

    def append(self, element):
        return Path(self.nodes + (element, ))

    def solvable(self):
        #NOTE: just checks for uniqueness for now
        #TODO: proper conflict checking
        return len(self.nodes) == len(set(self.nodes)) 

    def length(self):
        return len(self.nodes)
