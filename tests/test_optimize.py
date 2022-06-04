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
        gcc_o2 = yatuner.compilers.Gcc(infiles=['samples/euler.c'],
                                       outfile='build/euler',
                                       adds='-O2')
        gcc_o0 = yatuner.compilers.Gcc(infiles=['samples/euler.c'],
                                       outfile='build/euler')
        optimizer = yatuner.optimizers.BayesianOptimizer(gcc, goal='time')
        optimizer.optimize(20)
        gcc_o2.execute()
        # times = []
        # for i in range(5):
        #     time = yatuner.utils.timing(yatuner.utils.get_executable(gcc_o2.outfile))
        #     times.append(time)
        # times.sort()
        # time = sum(times[1:-1]) / 3
        time = yatuner.utils.timing(yatuner.utils.get_executable(gcc_o2.outfile))
        print("-O2 time: " + str(time))
        time = yatuner.utils.timing(yatuner.utils.get_executable(gcc_o0.outfile))
        print("-O0 time: " + str(time))

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