
import unittest
import tunemake
import os

class TestGccCompile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dummy(self):
        tunemake.gcc_compile(infile='dummy.c', outfile='dummy')

    def test_hello_world(self):
        tunemake.gcc_compile(infile='hello_world.c', outfile='hello_world')


if __name__ == '__main__':
    unittest.main()