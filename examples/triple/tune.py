import logging
import os
import yatuner

src = './src/triple.cpp'
out = './build/triple.exe'
metric = 'cpu-cycles'

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


tuner = yatuner.Tuner(comp, run, gcc.fetch_optimizers(),
                      gcc.fetch_parameters())

tuner.initialize()
tuner.test_run(num_samples=100, warmup=20)
tuner.hypotest_optimizers(num_samples=5)
tuner.hypotest_parameters(num_samples=5)
tuner.optimize(num_samples=10)
tuner.run(num_samples=50)