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

import yatuner
import unittest


class TestCompiler(unittest.TestCase):
    def test_gcc(self):
        src = 'tests/src/test.c'
        out = 'tests/build/test'

        gcc = yatuner.compiler.Gcc(src, out, cc='gcc')
        print(gcc.fetch_parameters())
        
class TestOptimizer(unittest.TestCase):
    def test_initialize(self):
        optimizer = yatuner.optimizer.Optimizer()
        optimizer.initialize()