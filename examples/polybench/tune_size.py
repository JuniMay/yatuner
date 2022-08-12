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
base = '-Os'
build_dir = './build_size'
workspace_dir = './workspace_size'

if not os.path.isdir(build_dir):
    os.mkdir(build_dir)

if not os.path.isdir(workspace_dir):
    os.mkdir(workspace_dir)

optimizers = set(yatuner.utils.fetch_gcc_optimizers(cc=cc)).difference(
    yatuner.utils.fetch_gcc_enabled_optimizers(options=base))
optimizers.remove('-fipa-pta')
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

        lm = '-lm'

        res = yatuner.utils.execute(
            f'{cc} {options} polybench/utilities/polybench.c '
            f'{case_dir}/{case_name}.c {lm} -o '
            f'{build_dir}/{case_name}.exe')

        if res['returncode'] != 0:
            raise RuntimeError(res['stderr'])

    def run():
        return yatuner.utils.fetch_size(f'{build_dir}/{case_name}.exe')

    def perf():
        raise NotImplementedError()

    tuner = yatuner.Tuner(comp,
                          run,
                          optimizers,
                          parameters,
                          perf,
                          workspace=f'{workspace_dir}/{case_name}.db',
                          log_level=logging.DEBUG,
                          norm_range=0.99,
                          deterministic=True)

    logger.info(f'[bold]Performing Optimization on {case_dir}[/]')

    tuner.initialize()
    tuner.test_run(num_samples=1, warmup=0)
    tuner.hypotest_optimizers(num_samples=1)
    tuner.hypotest_parameters(num_samples=1)
    tuner.optimize(num_samples=1, num_epochs=60)

    tuner.run(num_samples=1)
