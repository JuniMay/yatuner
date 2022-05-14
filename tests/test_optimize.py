import yatuner
import unittest
import os


class TestOptimize(unittest.TestCase):
    def test_bayesian(self):
        gcc = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
                                   outfile='tests/build/euler')

        optimizer = yatuner.optimizers.BayesianOptimizer(gcc)
        optimizer.optimize(15)

    def test_benchmark(self):
        yatuner.compilers.Gcc(
            stage='c',
            infiles=['tests/benchmarks/polybench/utilities/polybench.c'],
            outfile='tests/build/polybench.o',
            inc_dirs=['tests/benchmarks/polybench/utilities']).execute()

        gcc = yatuner.compilers.Gcc(
            infiles=[
                'tests/build/polybench.o',
                'tests/benchmarks/polybench/linear-algebra/kernels/3mm/3mm.c'
            ],
            outfile='tests/build/3mm',
            inc_dirs=[
                'tests/benchmarks/polybench/utilities',
                'tests/benchmarks/polybench/linear-algebra/kernels/3mm'
            ])

        optimizer = yatuner.optimizers.BayesianOptimizer(gcc)
        optimizer.optimize(15)