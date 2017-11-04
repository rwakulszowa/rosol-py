from itertools import groupby
import json

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
        Returns a VersionedPackage with a given name:version
        or None if doesn't exist
        """
        by_name = self.packages.get(name)
        if by_name:
            by_version = by_name.get(version)
            return by_version  # VersionedPackage | None
        else:
            return None


class VersionedPackage(object):
    def __init__(self, name, version, dependencies):
        self.name = name
        self.version = version
        self.dependencies = dependencies  # `*` dependencies
    

class Dependency(object):
    def to_json(self):
        d = self.__dict__
        d["kind"] = self.__class__.__name__
        return d


class Set(Dependency):
    def __init__(self, name, candidates):
        self.name = name
        self.candidates = candidates


class Range(Dependency):
    def __init__(self, name, lower, upper):
        self.name = name
        self.lower = lower
        self.upper = upper

