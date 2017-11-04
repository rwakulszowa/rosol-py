import unittest
import doctest

import node
import package
import path
import utils

suite = unittest.TestSuite()

for mod in [node, path, utils, package]:
    suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)
