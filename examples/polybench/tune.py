import logging
import pathlib
import yatuner
import os

build_dir = './build'
workspace_dir = './workspace'
metric = 'cpu-cycles'

if not os.path.isdir(build_dir):
    os.mkdir(build_dir)

if not os.path.isdir(workspace_dir):
    os.mkdir(workspace_dir)

gcc = yatuner.Gcc(src='',
                  out='',
                  cc='gcc',
                  params_def_path='../params.def',
                  template='{cc} {options} {src} -o {out}')

benchmark_list = []
for path in pathlib.Path('./polybench/').rglob('*.c'):
    path = str(path)
    if 'utilities' in path:
        continue

    case_dir = path.rsplit('/', 1)[0]
    case_name = case_dir.rsplit('/', 1)[1]
    benchmark_list.append((case_dir, case_name))

for case_dir, case_name in benchmark_list:

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

        options += f'-I polybench/utilities -I {case_dir} '
        gcc.compile(
            options,
            src=f'polybench/utilities/polybench.c {case_dir}/{case_name}.c',
            out=f'{build_dir}/{case_name}.exe')

    def run():
        return yatuner.utils.fetch_perf_stat(
            f'{build_dir}/{case_name}.exe')[metric] / 1000

    tuner = yatuner.Tuner(comp,
                          run,
                          gcc.fetch_optimizers(),
                          gcc.fetch_parameters(),
                          f'{workspace_dir}/{case_name}.db',
                          log_level=logging.INFO)
    
    logging.getLogger('PolyBench').info(
        f'Performing Optimization on {case_dir}')

    tuner.initialize()
    tuner.test_run(num_samples=100, warmup=20)
    tuner.hypotest_optimizers(num_samples=5)
    tuner.hypotest_parameters(num_samples=5)
    tuner.optimize(num_samples=10, num_epochs=60)
    tuner.run(num_samples=50)
