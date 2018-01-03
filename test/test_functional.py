import unittest

from rosol.package import Repository, SimpleVersionedPackage as Package, Set
from rosol import node, path

class FunctionalTest(unittest.TestCase):
    
    def setUp(self):
        pass
        #TODO: assert cache is clean

    def tearDown(self):
        pass
        #TODO: clear cache

    def test_simple(self):
        repo = Repository([
            Package("B", 1, []),
            Package("A", 1, [Set("B", [1])])])

        root = repo.get("A", 1).into_node(repo)
        result = root.resolve()

        self.assertEqual(
            result.paths,
            [
                path.Path([
                    node.Simple("A-1"),
                    node.Simple("B-1")])])

    def test_circular(self):
        repo = Repository([
            Package("A", 1, [Set("B", [1])]),
            Package("B", 1, [Set("A", [1])])])

        root = repo.get("A", 1).into_node(repo)
        result = root.resolve()

        self.assertEqual(
            result.paths,
            [])
