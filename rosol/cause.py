class Cause(object):
    def __init__(self, nodes):
        self.nodes = tuple(nodes)

    @classmethod
    def empty(cls):
        return cls(tuple())

    def above(self, node):
        return self._pop(node) if self._is_unique(node) else self

    def _pop(self, node):
        return Cause(
            n
            for n in self.nodes
            if n is not node)

    def _is_unique(self, node):
        return self.nodes.count(node) is 1

    def add(self, node):
        return self if self._has(node) else self._add(node)

    def _add(self, node):
        return Cause(
            self.nodes + (node, ))

    def _has(self, node):
        return node in self.nodes

