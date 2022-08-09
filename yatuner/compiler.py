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

from typing import Dict, List, Tuple
from abc import abstractmethod
import re
import subprocess
import yatuner
import ast


class Compiler(object):

    @abstractmethod
    def compile(self, options) -> None:
        raise NotImplementedError()

    @abstractmethod
    def fetch_version(self) -> Tuple[int]:
        raise NotImplementedError()

    @abstractmethod
    def version_str(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def fetch_optimizers(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def fetch_params(self) -> Dict[str, Tuple[int, int]]:
        raise NotImplementedError()

    @abstractmethod
    def fetch_execute_cmd(self) -> str:
        raise NotImplementedError()


class Gcc(Compiler):

    def __init__(self,
                 src: str,
                 out: str,
                 cc='gcc-9',
                 params_def_path='params.def',
                 template='{cc} {options}  -o {out} {src}') -> None:
        self.src = src
        self.out = out
        self.cc = cc
        self.template = template
        self.params_def_path = params_def_path

        self.version = None
        self.params = None
        self.optimizers = None

    def fetch_version(self) -> Tuple[int]:

        if self.version is not None:
            return self.version

        ver = re.search(
            r'([0-9]+)[.]([0-9]+)[.]([0-9]+)',
            subprocess.check_output([self.cc, '--version']).decode())
        if ver:
            self.version = tuple(map(int, ver.group(1, 2, 3)))
        else:
            self.version = None

        return self.version

    def version_str(self) -> str:
        if self.version is None:
            self.fetch_version()

        res = 'gcc {}.{}.{}'.format(self.version[0], self.version[1],
                                    self.version[2])

        return res

    def fetch_optimizers(self) -> List[str]:
        if self.optimizers is not None:
            return self.optimizers

        opt, _ = subprocess.Popen([self.cc, '--help=optimizers'],
                                  stdout=subprocess.PIPE).communicate()

        self.optimizers = re.findall(r'^  (-f[a-z0-9-]+) ', opt.decode(), re.M)

        return self.optimizers

    def fetch_parameters(self) -> Dict[str, Tuple[int, int, int]]:
        if self.params is not None:
            return self.params

        params_str, _ = subprocess.Popen([self.cc, '--help=params'],
                                         stdout=subprocess.PIPE).communicate()

        regex = r'^  --param=([a-z-]+)'  # TODO: fix for gcc-10

        if (self.fetch_version()[0] < 10):
            regex = r'^  ([a-z-]+)'

        raw_params = re.findall(regex, params_str.decode(), re.M)
        self.params = {}

        params_def_file = open(self.params_def_path)
        params_def = params_def_file.read()
        for m in re.finditer(r'DEFPARAM *\((([^")]|"[^"]*")*)\)', params_def):
            param_def_str = (
                m.group(1)  #
                .replace('GGC_MIN_EXPAND_DEFAULT', '30')  #
                .replace('GGC_MIN_HEAPSIZE_DEFAULT', '4096')  #
                .replace('50 * 1024 * 1024', '52428800')  #
                .replace('128 * 1024 * 1024', '134217728')  #
                .replace('INT_MAX', '2147483647'))  #

            # print(param_def_str)

            param, desc, default, r_min, r_max = ast.literal_eval(
                '[' + param_def_str.split(',', 1)[1] + ']')

            if param not in raw_params:
                continue

            if r_max == 0:
                r_max = min(default * 10, 2147483647)

            self.params[param] = (r_min, r_max, default)

        params_def_file.close()

        return self.params

    def compile(self, options='', src=None, out=None) -> None:

        if src is not None:
            self.src = src

        if out is not None:
            self.out = out

        command = self.template.format(cc=self.cc,
                                       options=options,
                                       out=self.out,
                                       src=self.src)
        # print(command)
        res = yatuner.utils.execute(command)

        if res['returncode'] != 0:
            raise RuntimeError(res['stderr'])

    def filter_options(self) -> None:
        # TODO
        raise NotImplementedError()

    def fetch_execute_cmd(self) -> str:
        return self.out