import json

from utils import flatten


class Node(object):
    def dumps(self):
        return json.dumps(
            self,
            indent = 4,
            default = lambda n: n.to_json() if hasattr(n, "to_json") else n)


class Simple(Node):

    def __init__(self, name, dependency):
        self.name = name
        self.dependency = dependency

    def id(self):
        return self.name

    def __repr__(self):
        return "{}: {}".format(
            self.id(),
            self.dependency.id())

    def to_json(self):
        return {
            "id": self.id(),
            "dep": self.dependency }

    def paths(self, acc):
        """ Get all possible paths from self to Nil.
        FIXME: generators, check for circular lists
        """
        return self.dependency.paths([
            prefix + (self.name, )
            for prefix in acc])


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

    def paths(self, acc):
        updated = [
            prefix + (self, )
            for prefix in acc]

        return flatten([
            child.paths(updated)
            for child in self.children])


class And(Complex):
    @staticmethod
    def operator():
        return " * "


class Or(Complex):
    @staticmethod
    def operator():
        return " + "


class Nil(Node):
    @staticmethod
    def id():
        return "()"

    @staticmethod
    def to_json():
        return None

    @staticmethod
    def paths(acc):
        return acc
