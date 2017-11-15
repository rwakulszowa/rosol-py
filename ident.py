class Ident(object):
    def __eq__(self, other):
        return type(self) == type(other) and self._id() == other._id()

    def __hash__(self):
        return hash(self._id())

    @classmethod
    def are_conflicting(cls, ident_set):
        """
        Checks for conflicts in multiple `Ident` instances
        """
        return cls._are_conflicting(ident_set)


class Simple(Ident):
    """
    String-like ident for demonstration purposes
    """
    def __init__(self, name):
        self.name = name

    def _id(self):
        return self.name

    def __repr__(self):
        return self.name

    @classmethod
    def _are_conflicting(cls, ident_set):
        """
        >>> A, B = [Simple(name) for name in ["A", "B"]]
        >>> Simple.are_conflicting([A, B])
        False
        >>> Simple.are_conflicting([A, B, A])
        True
        """
        return len(ident_set) != len(set(ident_set))

