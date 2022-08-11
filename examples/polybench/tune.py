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
import pathlib
import yatuner
import os

cc = 'gcc'
base = '-O3'
build_dir = './build'
workspace_dir = './workspace'
metric = 'duration_time'

if not os.path.isdir(build_dir):
    os.mkdir(build_dir)

if not os.path.isdir(workspace_dir):
    os.mkdir(workspace_dir)

optimizers = set(yatuner.utils.fetch_gcc_optimizers(cc=cc)).difference(
    yatuner.utils.fetch_gcc_enabled_optimizers(options=base))
parameters = yatuner.utils.fetch_gcc_parameters(cc=cc)

benchmark_list = []
for path in pathlib.Path('./polybench/').rglob('*.c'):
    path = str(path)
    if 'utilities' in path:
        continue

    case_dir = path.rsplit('/', 1)[0]
    case_name = case_dir.rsplit('/', 1)[1]
    benchmark_list.append((case_dir, case_name))

logger = logging.getLogger('polybench')
logger.setLevel(logging.INFO)

for case_dir, case_name in benchmark_list:

    def comp(optimizers, parameters, additional):
        options = '-DMEDIUM_DATASET '

        if additional is not None:
            options += f'{additional} '
        else:
            options += f'{base} '

        if optimizers is not None:
            for optimizer in optimizers:
                options += f'{optimizer} '

        if parameters is not None:
            for parameter, val in parameters.items():
                options += f'--param={parameter}={val} '

        options += f'-I {case_dir} -I polybench/utilities '

        lm = ''

        if case_name in ['cholesky', 'gramschmidt', 'correlation']:
            lm = '-lm'

        res = yatuner.utils.execute(
            f'{cc} {options} {lm} polybench/utilities/polybench.c '
            f'{case_dir}/{case_name}.c -o '
            f'{build_dir}/{case_name}.exe')

        if res['returncode'] != 0:
            raise RuntimeError(res['stderr'])

    def run():
        return yatuner.utils.fetch_perf_stat(
            f'{build_dir}/{case_name}.exe')[metric] / 1000

    def perf():
        return yatuner.utils.fetch_perf_stat(f'{build_dir}/{case_name}.exe')

    tuner = yatuner.Tuner(comp,
                          run,
                          optimizers,
                          parameters,
                          perf,
                          workspace=f'{workspace_dir}/{case_name}.db',
                          log_level=logging.INFO,
                          norm_range=0.99)

    logger.info(f'Performing Optimization on {case_dir}')

    tuner.initialize()
    tuner.test_run(num_samples=200, warmup=10)
    tuner.hypotest_optimizers(num_samples=5)
    tuner.hypotest_parameters(num_samples=5)
    # tuner.optimize(num_samples=10, num_epochs=60)
    tuner.optimize_linUCB(alpha=0.25,
                          num_bins=30,
                          num_epochs=200,
                          nth_choice=4,
                          metric=metric)

    tuner.run(num_samples=50)
    tuner.plot_data()
