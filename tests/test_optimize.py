import yatuner
import unittest
from bitarray import bitarray
import os


class TestOptimize(unittest.TestCase):
    def test_bayesian(self):
        gcc = yatuner.compiler.Gcc(infiles=['samples/euler.c'],
                                   outfile='samples/euler')

        optimizer = yatuner.optimizer.BayesianOptimizer(gcc)
        optimizer.optimize(15)
