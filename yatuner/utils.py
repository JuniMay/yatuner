# -*- coding: utf-8 -*-

# Copyright (c) 2022 Synodic Month, Juni May
# yaTuner is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

from itertools import count
import subprocess
import re
import os
from typing import Any, Dict
import numpy as np
import platform


def execute(command) -> Dict[str, Any]:
    """Execute given command.

    Args:
        command: command to be executed.

    """
    # TODO: time & memory limit
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(timeout=30)
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
    perf_command = ('perf stat -x,'
                    ' -e branch-instructions '
                    ' -e branch-misses '
                    ' -e bus-cycles '
                    ' -e cache-misses '
                    ' -e cache-references '
                    ' -e duration_time' 
                    ' -e cpu-cycles '
                    ' -e instructions '
                    ' -e ref-cycles '
                    ' -e alignment-faults '
                    ' -e bpf-output '
                    ' -e context-switches '
                    ' -e cpu-clock '
                    ' -e cpu-migrations '
                    ' -e dummy '
                    ' -e emulation-faults '
                    ' -e major-faults '
                    ' -e minor-faults '
                    ' -e page-faults '
                    ' -e task-clock '
                    ' -e duration_time '
                    ' -e user_time '
                    ' -e system_time '
                    # ' -e L1-dcache-load-misses '
                    # ' -e L1-dcache-loads '
                    # ' -e L1-dcache-stores '
                    # ' -e L1-icache-load-misses '
                    # ' -e branch-load-misses '
                    # ' -e branch-loads '
                    # ' -e dTLB-load-misses '
                    # ' -e dTLB-loads '
                    # ' -e dTLB-store-misses '
                    # ' -e dTLB-stores '
                    # ' -e iTLB-load-misses '
                    # ' -e slots '
                    # ' -e topdown-bad-spec '
                    # ' -e topdown-be-bound '
                    # ' -e topdown-fe-bound '
                    # ' -e topdown-retiring '
                    # ' -e msr/pperf/ '
                    # ' -e msr/smi/ '
                    ' -e msr/tsc/ '+ command)  # TODO: auto detect events

    res = execute(perf_command)

    if res['returncode'] != 0:
        raise RuntimeError(res['stderr'])
    else:
        counter_tuples = []
        for line in res['stderr'].splitlines():
            stat = line.split(',')
            counter_tuples.append((stat[2], stat[0]))
        # print(counter_tuples)
        counter_dict = dict(
            (x, 0 if y in ['<not supported>', '<not counted>'] else float(y))
            for (x, y) in counter_tuples)

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