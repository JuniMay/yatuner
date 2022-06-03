import yatuner
import unittest
import os


class TestOptimize(unittest.TestCase):
    def test_bayesian_size(self):
        # gcc = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
        #                             outfile='tests/build/euler')
        # gcc_os = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
        #                                outfile='tests/build/euler',
        #                                adds='-Os')
        # convenient for Synodic to test on win
        gcc = yatuner.compilers.Gcc(infiles=['samples/euler.c'],
                                    outfile='build/euler')
        gcc_os = yatuner.compilers.Gcc(infiles=['samples/euler.c'],
                                       outfile='build/euler',
                                       adds='-Os')
        optimizer = yatuner.optimizers.BayesianOptimizer(gcc)
        optimizer.optimize(15)
        gcc_os.execute()
        print("-Os size: " + str(gcc_os.fetch_size()))

    def test_bayesian_time(self):
        # gcc = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
        #                             outfile='tests/build/euler')
        # gcc_os = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
        #                                outfile='tests/build/euler',
        #                                adds='-Os')
        # convenient for Synodic to test on win
        gcc = yatuner.compilers.Gcc(infiles=['samples/euler.c'],
                                    outfile='build/euler')
        gcc_o3 = yatuner.compilers.Gcc(infiles=['samples/euler.c'],
                                       outfile='build/euler',
                                       adds='-O3')
        optimizer = yatuner.optimizers.BayesianOptimizer(gcc, goal='time')
        optimizer.optimize(10)
        gcc_o3.execute()
        print("-O3 time: " + str(yatuner.utils.timing(gcc_o3.outfile)))

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

if __name__ == '__main__':
    unittest.main()