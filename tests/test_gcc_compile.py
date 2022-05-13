import unittest
import yatuner
import os


class TestGccCompile(unittest.TestCase):
    def test_dummy(self):
        gcc = yatuner.compiler.Gcc(infiles=['samples/dummy.c'],
                                   outfile='samples/dummy')
        gcc.execute()

    def test_hello_world(self):
        gcc = yatuner.compiler.Gcc(infiles=['samples/hello_world.c'],
                                   outfile='samples/hello_world')
        gcc.execute()


if __name__ == '__main__':
    unittest.main()