import unittest
import yatuner
import os


class TestGccCompile(unittest.TestCase):
    def test_dummy(self):
        gcc = yatuner.compilers.Gcc(infiles=['tests/samples/dummy.c'],
                                   outfile='tests/build/dummy')
        gcc.execute()

    def test_hello_world(self):
        gcc = yatuner.compilers.Gcc(infiles=['tests/samples/hello_world.c'],
                                   outfile='tests/build/hello_world')
        gcc.execute()


if __name__ == '__main__':
    unittest.main()