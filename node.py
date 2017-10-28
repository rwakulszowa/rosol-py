import json


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


class And(Node):
    def __init__(self, children):
        self.children = children

    def id(self):
        inner = " * ".join(child.id() for child in self.children)
        return "({})".format(inner)

    def to_json(self):
        return {
            "id": self.id(),
            "dep": self.children }


class Or(Node):
    def __init__(self, children):
        self.children = children

    def id(self):
        inner = " + ".join(child.id() for child in self.children)
        return "({})".format(inner)


    def to_json(self):
        return {
            "id": self.id(),
            "dep": self.children }


class Nil(Node):
    @staticmethod
    def id():
        return "()"

    @staticmethod
    def to_json():
        return None
