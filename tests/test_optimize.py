from yatuner.optimize import gen_optimization_option_list
from yatuner.compiler import Gcc
from yatuner.utils import fetch_file_size
import unittest
from bitarray import bitarray
import os

class TestOptimize(unittest.TestCase):
    def test_hello_world(self):
        option_list = gen_optimization_option_list(bitarray('10101110111111100001011010101010101010101010101010101011'))
        print(option_list)
        in_file = os.path.dirname(os.getcwd()).replace('/', '\\') + r"\tests\samples\hello_world.c"
        out_file = os.path.dirname(os.getcwd()).replace('/', '\\') + r"\tests\samples\hello_world.exe"
        compiler = Gcc(infile_list=[in_file], outfile=out_file, f_option_list=option_list)
        compiler.execute()
        print(fetch_file_size(out_file))