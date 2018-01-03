import unittest
import doctest

from rosol import node, path, utils, package, ident, cache

suite = unittest.TestSuite()

for mod in [node, path, utils, package, ident, cache]:
    suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)
