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

import logging
import os
import yatuner

src = './src/triple.cpp'
out = './build/triple.exe'
metric = 'duration_time'

gcc = yatuner.Gcc(src=src,
                  out=out,
                  cc='g++',
                  params_def_path='../params.def',
                  template='{cc} {options} {src} -o {out}')

if not os.path.isdir('./build'):
    os.mkdir('./build')


def comp(optimizers, parameters, additional):
    options = ''

    if additional is not None:
        options = f'{additional} '
    else:
        options = '-O3 '

    if optimizers is not None:
        for optimizer in optimizers:
            options += f'{optimizer} '

    if parameters is not None:
        for parameter, val in parameters.items():
            options += f'--param={parameter}={val} '

    gcc.compile(options=options)


def run():
    return yatuner.utils.fetch_perf_stat(
        gcc.fetch_execute_cmd())[metric] / 1000


def perf():
    return yatuner.utils.fetch_perf_stat(gcc.fetch_execute_cmd())


tuner = yatuner.Tuner(comp,
                      run,
                      gcc.fetch_optimizers(),
                      gcc.fetch_parameters(),
                      call_perf=perf,
                      norm_range=None)

tuner.initialize()
tuner.test_run(num_samples=50, warmup=0)
tuner.hypotest_optimizers(num_samples=5)
tuner.hypotest_parameters(num_samples=5)
# tuner.optimize(num_samples=10)
tuner.optimize_linUCB(alpha=0.25, num_bins=30, num_epochs=200, nth_choice=4)
tuner.run(num_samples=50)
tuner.plot_data()