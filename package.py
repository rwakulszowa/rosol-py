from itertools import groupby
import json

import ident
import node
from utils import dumps


class Repository(object):
    def __init__(self, packages):
        def by_name(pkgs):
            return groupby(
                pkgs,
                lambda pkg: pkg.name)

        def by_version(pkgs):
            return groupby(
                pkgs,
                lambda pkg: pkg.version)

        #TODO: store by_version as a sorted list instead?
        self.packages = {
            name: {
                version: next(grp2)
                for version, grp2 in by_version(grp1)}
            for name, grp1 in by_name(packages)}

    def dumps(self):
        return dumps(self)

    def get(self, name, version):
        """
        Returns a SimpleVersionedPackage with a given name:version
        or None if doesn't exist
        """
        by_name = self.packages.get(name)
        if by_name:
            by_version = by_name.get(version)
            return by_version  # SimpleVersionedPackage | None
        else:
            return None

    def get_hits(self, keys):
        """
        Same as `get`, but for a list of keys and with misses filtered out
        """
        got = (
            self.get(*key)
            for key in keys)

        return (
            pkg
            for pkg in got
            if pkg is not None)


class SimpleVersionedPackage(object):
    NodeCls = node.Simple
    IdentCls = ident.Simple

    def __init__(self, name, version, dependencies):
        self.name = name
        self.version = version
        self.dependencies = dependencies  # `*` dependencies

    def __repr__(self):
        return "{}: {}".format(
            self.id(),
            self.dependencies)

    def id(self):
        return self.IdentCls(
            "{}-{}".format(
                self.name,
                self.version))

    def into_node(self, repo):
        """
        Convert into a `Node`

        Returns a `node.Simple` with a lazily resolvable `node.Dependency`
        >>> A1 = SimpleVersionedPackage("A", 1, [])
        >>> B1 = SimpleVersionedPackage("B", 1, [Set("A", [1])])
        >>> repo = Repository([A1, B1])
        >>> A1.into_node(repo) == node.Simple("A-1")
        True
        >>> B1.into_node(repo) == node.Simple("B-1", node.And([node.Simple("A-1")]))
        True
        """
        def make_dependency_node():
            # This wrapper makes the resolution lazy on Simple nodes
            yield node.And(
                dep.into_node(repo)
                for dep in self.dependencies)

        dependency = node.Dependency(make_dependency_node()) if len(self.dependencies) is not 0 else node.NilDependency

        return self.NodeCls(
            self.id(),
            dependency)


class Dependency(object):
    def to_json(self):
        d = self.__dict__
        d["kind"] = self.__class__.__name__
        return d

    def resolve(self, repo):
        """
        Returns existing packages from a `repo` matching the precondition
        >>> A1, A2, A3 = [
        ...     SimpleVersionedPackage("A", num, [])
        ...     for num in (1, 2, 3)]
        >>> repo = Repository([A1, A2, A3])
        >>> dep = Set("A", [1, 3])
        >>> list(dep.resolve(repo)) == [A1, A3]
        True
        >>> dep = Range("A", 1, 2)
        >>> list(dep.resolve(repo)) == [A1, A2]
        True
        """
        return repo.get_hits(
            self.keys())

    def into_node(self, repo):
        """
        Convert into a `Node`
        >>> A1 = SimpleVersionedPackage("A", 1, [])
        >>> repo = Repository([A1])
        >>> dep = Set("A", [1])
        >>> dep.into_node(repo) == node.Or([node.Simple("A-1")])
        True
        """
        return node.Or(
            dep.into_node(repo)
            for dep in self.resolve(repo))


class Set(Dependency):
    def __init__(self, name, candidates):
        self.name = name
        self.candidates = candidates

    def __repr__(self):
        return "{}: {}".format(
            self.name,
            self.candidates)

    def keys(self):
        return [
            (self.name, version)
            for version in self.candidates]

        
class Range(Dependency):
    def __init__(self, name, lower, upper):
        self.name = name
        self.lower = lower
        self.upper = upper

    def __repr__(self):
        return "{}: <{}, {}>".format(
            self.name,
            self.lower,
            self.upper)

    def keys(self):
        return [
            (self.name, version)
            for version in range(self.lower, self.upper + 1)]
