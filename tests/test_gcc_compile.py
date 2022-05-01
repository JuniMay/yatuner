import unittest
import yatuner
import os


class TestGccCompile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dummy(self):
        yatuner.gcc_compile(infile='samples/dummy.c', outfile='samples/dummy')

    def test_hello_world(self):
        yatuner.gcc_compile(infile='samples/hello_world.c',
                            outfile='samples/hello_world')


if __name__ == '__main__':
    unittest.main()