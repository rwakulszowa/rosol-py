import ident
from path import Path
from utils import *
from cache import instance as CACHE

#TODO: split into multiple files
#TODO: leave only simple tests here, move proper tests to a separate file


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


class NilDependency(Dependency):

    @staticmethod
    def resolve():
        return Nil


class Node(object):
    PathCls = Path
    IdentCls = ident.Simple

    def dumps(self):
        return dumps(self)

    def resolve(self, prefix=None):
        """ Get all possible paths from self to Nil.

        Filters out unsolvable paths, doesn't hang on circular dependencies.
        >>> A = Simple("A")
        >>> list(A.resolve().paths)
        [Path: (A,)]

        >>> B = Simple("B", Dependency.make(A))
        >>> list(B.resolve().paths)
        [Path: (B, A)]

        >>> B.resolve(Path([A])).is_success()  # A present in prefix and dependencies
        False

        >>> C = Simple("C")
        >>> AndAC = And([A, C])
        >>> list(AndAC.resolve().paths)
        [Path: (A, C)]

        >>> AndAC.resolve(Path([A])).is_success()  # A present in prefix
        False

        >>> D = Simple("D")
        >>> OrCD = Or([C, D])
        >>> list(OrCD.resolve(Path([A])).paths)
        [Path: (A, C), Path: (A, D)]

        >>> list(OrCD.resolve(Path([A, C])).paths)  # C would cause a conflict, D is fine
        [Path: (A, C, D)]
        """
        #TODO: make this function great again -> it's kinda useless now
        prefix = prefix or self.PathCls.empty()

        return self._resolve(prefix)

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

    def _resolve(self, prefix):
        """
        >>> A = Simple("A")

        >>> adin = A._resolve(Path.empty())
        >>> adin.is_success()
        True
        >>> list(adin.paths)
        [Path: (A,)]

        >>> dwa = A._resolve(Path([A]))
        >>> dwa.is_success()
        False
        """
        circular = prefix.has(self)
        new_prefix = prefix.append(self)

        if not new_prefix.solvable():
            # The conflict must be caused by self
            # NOTE: this branch doesn't cache failures,
            # because it is either trivial or already cached
            causes = { self }
            return Result([], causes)  # Failure
        else:
            if circular:
                return Success(self, [new_prefix], set())  # Success with no causes
            else:
                ans = self.dependency.resolve().resolve(new_prefix)
                new_causes = ans.causes - { self }
                if not ans.is_success():
                    CACHE.set(ans.causes | { self })
                return Result(ans.paths, new_causes)


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

    @staticmethod
    def _megapath(prefix, suffixes):

        elements = [prefix] + [
            suffix - prefix
            for suffix in suffixes]

        return Path.chain(elements)

    def _resolve(self, prefix):
        """
        >>> A = Simple("A")
        >>> B = Simple("B")
        >>> C = And([A, B])
        >>> D = Simple("D")
        >>> E = Simple("E", Dependency.make(A))

        >>> adin = C._resolve(Path.empty())
        >>> adin.is_success()
        True
        >>> list(adin.paths)
        [Path: (A, B)]

        >>> dwa = C._resolve(Path([D]))
        >>> dwa.is_success()
        True
        >>> list(dwa.paths)
        [Path: (D, A, B)]

        >>> tri = C._resolve(Path([A]))
        >>> tri.is_success()
        False
        """
        results_per_child = [
            child.resolve(prefix)
            for child in self.children]

        causes = Result.concat_causes(results_per_child)

        successes, failures = split(
            results_per_child,
            lambda x: x.is_success())

        successes, failures = list(successes), list(failures)

        if len(failures) is not 0:
            # If any subpath failed, fail early
            return Result(
                [],
                causes)

        paths_per_child = [
            result.paths
            for result in results_per_child]

        megapaths = [
            self._megapath(
                prefix,
                selection)
            for selection in selections(paths_per_child)]

        return Result(
            [
                megapath
                for megapath in megapaths
                if megapath.solvable()],
            causes)


class Or(Complex):
    @staticmethod
    def operator():
        return " + "
    
    def _resolve(self, prefix):
        """
        >>> A = Simple("A")
        >>> B = Simple("B")
        >>> C = Or([A, B])
        >>> D = Simple("D")

        >>> adin = C._resolve(Path.empty())
        >>> adin.is_success()
        True
        >>> list(adin.paths)
        [Path: (A,), Path: (B,)]

        >>> dwa = C._resolve(Path([D]))
        >>> dwa.is_success()
        True
        >>> list(dwa.paths)
        [Path: (D, A), Path: (D, B)]
        """
        subresults = list(
            child.resolve(prefix)
            for child in self.children)
        
        causes = Result.concat_causes(subresults)

        return Result(
            flatten([
                result.paths
                for result in subresults]),
            causes)


class Nil(Node):
    @staticmethod
    def id():
        return "()"

    @staticmethod
    def to_json():
        return None

    @classmethod
    def _resolve(cls, prefix):
        return Result([prefix], set())

    @classmethod
    def resolve(cls, prefix=None):
        #FIXME: just instantiate Nil nodes as well
        prefix = prefix or Path.empty()
        return cls._resolve(prefix)


class Result(object):

    def __init__(self, paths, causes):
        self.paths = list(paths)  #FIXME: use generators
        self.causes = causes

    def is_success(self):
        return len(self.paths) is not 0

    def __repr__(self):
        return "{}: {} - {}".format(
            self.__class__.__name__,
            self.paths,
            self.causes)
    
    @staticmethod
    def concat_causes(results):
        ans = set()
        for result in results:
            ans |= result.causes
        return ans

