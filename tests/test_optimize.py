import yatuner
import unittest
import os


class TestOptimize(unittest.TestCase):
    def test_bayesian(self):
        gcc = yatuner.compiler.Gcc(infiles=['tests/samples/euler.c'],
                                   outfile='tests/samples/euler')

        optimizer = yatuner.optimizer.BayesianOptimizer(gcc)
        optimizer.optimize(15)

    def test_benchmark(self):
        gcc = yatuner.compiler.Gcc(
            infiles=[
                'tests/benchmarks/polybench/utilities/polybench.c',
                'tests/benchmarks/polybench/linear-algebra/kernels/3mm/3mm.c'
            ],
            outfile='tests/benchmarks/3mm',
            inc_dirs=[
                'tests/benchmarks/polybench/utilities',
                'tests/benchmarks/polybench/linear-algebra/kernels/3mm'
            ])

        optimizer = yatuner.optimizer.BayesianOptimizer(gcc)
        optimizer.optimize(15)