from itertools import count
import subprocess
import re
import os
from typing import Any, Dict
import numpy as np
import platform


def execute(command, time_limit=None, memory_limit=None) -> Dict[str, Any]:
    """Execute given command.

    Args:
        command: command to be executed.

    """
    # TODO: time & memory limit
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    returncode = p.returncode

    p.terminate()

    return {
        'returncode': returncode,
        'stdout': stdout.decode(),
        'stderr': stderr.decode(),
    }


def fetch_perf_stat(command) -> Dict[str, Any]:
    """Use `perf stat <command>` to analyze given program and get dict of counters.

    """
    perf_command = ('perf stat '
                    ' -e user_time ' + command)  # TODO: auto detect events

    res = execute(perf_command)
    # print(res['stderr'])

    if res['returncode'] != 0:
        raise RuntimeError(res['stderr'])
    else:
        counter_tuples = re.findall(
            (r'^\s+([\d.,]+|<not supported>+|<not counted>+)'
             r'[\sa-z]*?([0-9a-zA-Z-_/]+[:/]u)'), res['stderr'], re.M)
        counter_dict = dict(
            (y, 0 if x in ['<not supported>', '<not counted>'] else float(
                x.replace(',', ''))) for (x, y) in counter_tuples)

        return counter_dict


def ir2vec(llvm_ir, outfile, mode='fa', vocab='vocab.txt', level='p'):
    if (os.path.exists(outfile)):
        os.remove(outfile)
    command = (f'ir2vec -{mode} -vocab {vocab}'
               f' -o {outfile} -level {level} {llvm_ir}')
    res = execute(command)
    if (res['returncode'] != 0):
        raise RuntimeError(res)
    vec = np.genfromtxt(outfile)
    return vec


def generate_llvm(src, llvm_ir, llvm_compiler='clang') -> None:
    command = f'{llvm_compiler} -S -emit-llvm -o {llvm_ir} {src}'
    res = execute(command)
    if (res['returncode'] != 0):
        raise RuntimeError(res)


def fetch_src_feature(src: str,
                      llvm_ir=None,
                      outfile=None,
                      clean=False) -> np.array:
    if llvm_ir is None:
        llvm_ir = src + '.ll'
    if outfile is None:
        outfile = src + '.csv'

    llvm_compiler = ''

    if src.endswith(('.c')):
        llvm_compiler = 'clang'
    elif src.endswith(('.F')):
        llvm_compiler = 'flang'
    elif src.endswith(('.cpp', '.cc', '.cxx')):
        llvm_compiler = 'clang++'

    try:
        generate_llvm(src, llvm_ir, llvm_compiler)
    except RuntimeError as err:
        print('[ ERROR ] llvm-ir: ', err)  # TODO: print -> log

    try:
        vec = ir2vec(llvm_ir, outfile)
    except RuntimeError as err:
        print('[ ERROR ] ir2vec: ', err)

    if (clean):
        if (os.path.exists(llvm_ir)):
            os.remove(llvm_ir)

        if (os.path.exists(outfile)):
            os.remove(outfile)

    return vec

def fetch_arch() -> str:
    return platform.machine()