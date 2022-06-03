import unittest
import yatuner

class TestTiming(unittest.TestCase):
    def test_timing(self):

        gcc = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
                                    outfile='tests/build/euler')
        gcc.execute()
        t = yatuner.utils.timing('build/euler')
        print(f"Euler sieve time: {t}")