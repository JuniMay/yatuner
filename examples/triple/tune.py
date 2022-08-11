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

cc = 'g++'
src = './src/triple.cpp'
out = './build/triple.exe'
base = '-O3'
metric = 'duration_time'

if not os.path.isdir('./build'):
    os.mkdir('./build')

optimizers = set(yatuner.utils.fetch_gcc_optimizers(cc=cc)).difference(
    yatuner.utils.fetch_gcc_enabled_optimizers(options=base))
# optimizers.remove('-fipa-pta')
parameters = yatuner.utils.fetch_gcc_parameters(cc=cc)


def comp(optimizers, parameters, additional):
    options = ''

    if additional is not None:
        options = f'{additional} '
    else:
        options = f'{base} '

    if optimizers is not None:
        for optimizer in optimizers:
            options += f'{optimizer} '

    if parameters is not None:
        for parameter, val in parameters.items():
            options += f'--param={parameter}={val} '

    res = yatuner.utils.execute(f'{cc} {options} {src} -o {out}')
    if res['returncode'] != 0:
        raise RuntimeError(res['stderr'])


def run():
    return yatuner.utils.fetch_perf_stat(out)[metric] / 1000


def perf():
    return yatuner.utils.fetch_perf_stat(out)


tuner = yatuner.Tuner(comp,
                      run,
                      optimizers,
                      parameters,
                      call_perf=perf,
                      norm_range=0.99)

tuner.initialize()
tuner.test_run(num_samples=50, warmup=10)
tuner.hypotest_optimizers(num_samples=5, num_epochs=30)
tuner.hypotest_parameters(num_samples=5)
# tuner.optimize(num_samples=10, num_epochs=50)
tuner.optimize_linUCB(alpha=0.25,
                      num_bins=30,
                      num_epochs=200,
                      nth_choice=4,
                      metric=metric)
tuner.run(num_samples=50)
tuner.plot_data()