import os
import subprocess
from typing import List
from abc import abstractmethod

from yatuner import utils
from yatuner import errors


class Compiler(object):
    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError()


class Gcc(Compiler):
    #TODO: simplification, e.g. unify option
    def __init__(self,
                 stage: str = '',
                 infile_list: List[str] = [],
                 outfile: str = None,
                 w_option_list: List[str] = [],
                 f_option_list: List[str] = [],
                 lib_list: List[str] = [],
                 inc_list: List[str] = []):
        self.cmd = 'gcc'

        self.options = {
            'stage': '',
            'infile': '',
            'outfile': '',
            'w': '',
            'f': '',
            'lib': '',
            'inc': ''
        }

        if stage not in ['', 'c', 'E', 'S']:
            raise errors.InvalidOption()
        elif stage != '':
            self.options['stage'] = f' -{stage}'

        if outfile is not None:
            self.options['outfile'] = f' -o{outfile}'

        for infile in infile_list:
            self.options['infile'] += f' {infile}'

        for f_option in f_option_list:
            self.options['f'] += f' -f{f_option}'

        for w_option in w_option_list:
            self.options['w'] += f' -f{w_option}'

        for lib in lib_list:
            self.options['lib'] += f' -l{lib}'

        for inc in inc_list:
            self.options['inc'] += f' -i{inc}'

        # p = subprocess.Popen('gcc --version',
        #                      shell=True,
        #                      stdout=subprocess.PIPE)
        # p.wait()

        # print("Gcc version:")

        # print(p.communicate()[0])

    @abstractmethod
    def execute(self) -> None:
        self.cmd += self.options['stage'] + self.options['w'] + self.options[
            'f'] + self.options['lib'] + self.options['inc'] + self.options[
                'infile'] + self.options['outfile']
        utils.execute(self.cmd)