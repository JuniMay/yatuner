import random
import os
from compiler import Gcc
from utils import fetch_file_size
from bitarray import bitarray
from typing import List, NoReturn


def gen_optimization_option_list(option_flag: bitarray) -> List[str]:
    res: List[str] = []
    options = [option[:-1] for option in open("options.txt").readlines()]
    for i in range(len(option_flag)):
        if option_flag[i] == 1:
            res.append(options[i])

    return res


if __name__ == '__main__':
    option_list = gen_optimization_option_list(bitarray('10101110111111100001011010101010101010101010101010101011'))
    print(option_list)
    in_file = os.path.dirname(os.getcwd()).replace('/', '\\') + r"\tests\samples\hello_world.c"
    out_file = os.path.dirname(os.getcwd()).replace('/', '\\') + r"\tests\samples\hello_world.exe"
    compiler = Gcc(infile_list=[in_file], outfile=out_file, f_option_list=option_list)
    compiler.execute()
    print(fetch_file_size(out_file))
