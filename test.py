import unittest
import doctest

import node
import path
import utils

suite = unittest.TestSuite()

for mod in [node, path, utils]:
    suite.addTest(doctest.DocTestSuite(mod))

runner = unittest.TextTestRunner()
runner.run(suite)
