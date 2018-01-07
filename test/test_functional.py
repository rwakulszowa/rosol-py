import unittest

from rosol.cache import instance as CACHE
from rosol.package import Repository, SimpleVersionedPackage as Package, Set
from rosol import node, path

class FunctionalTest(unittest.TestCase):
    
    def setUp(self):
        CACHE.clear()

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

    def test_non_existent_package(self):

        repo = Repository([
            Package("A", 1, [Set("B", [1])])])

        root = repo.get("A", 1).into_node(repo)
        result = root.resolve()

        self.assertEqual(
            result.paths,
            [])

    def test_not_so_simple(self):

        repo = Repository([
            Package("A", 1, [
                Set("B", [1, 2])]),

            Package("B", 1, [
                Set("C", [1]),
                Set("D", [1, 2])]),

            Package("C", 1, []),

            Package("D", 1, [
                Set("C", [1])]),  # D1 <-> C1 -> circular dependency

            Package("D", 2, [
                Set("A", [1])]),  # D1 <-> A1 -> conflict

            Package("B", 2, [
                Set("E", [1])]),
            
            Package("E", 1, [])])

        root = repo.get("A", 1).into_node(repo)
        result = root.resolve()

        self.assertEqual(
            result.paths,
            [
                path.Path([
                    node.Simple("A-1"),
                    node.Simple("B-2"),
                    node.Simple("E-1")])])

