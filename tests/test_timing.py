import unittest
import yatuner


class TestTiming(unittest.TestCase):

    def test_timing(self):
        gcc = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
                                    outfile='tests/build/euler')
        # gcc = yatuner.compilers.Gcc(infiles=['samples/euler.c'],
        #                             outfile='build/euler')

        gcc.execute()
        for j in range(10):
            times = []
            for i in range(5):
                t = yatuner.utils.timing(
                    yatuner.utils.get_executable('tests/build/euler'))
                    # yatuner.utils.get_executable('build/euler'))
                times.append(t)
            times.sort()
            print(sum(times[1:-1]) / 3)
