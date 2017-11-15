import unittest
import doctest

import ident
import node
import package
import path
import utils

suite = unittest.TestSuite()

for mod in [node, path, utils, package, ident]:
    suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)
