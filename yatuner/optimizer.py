from copy import deepcopy
from inspect import Parameter
import os

import numpy as np
import yatuner
import logging

import GPyOpt

from rich.logging import RichHandler
from rich.progress import track
from scipy import stats
from matplotlib import pyplot as plt


class Optimizer:

    def __init__(self,
                 src: str = None,
                 out: str = None,
                 cc='gcc',
                 params_def_path='params.def',
                 template='{cc} {options}  -o {out} {src}',
                 use_vm=True,
                 cache_dir='yatuner.db') -> None:

        logging.basicConfig(level=logging.DEBUG,
                            format='[ %(name)s ] %(message)s',
                            handlers=[
                                RichHandler(level=logging.DEBUG,
                                            markup=True,
                                            show_path=False)
                            ])
        self.logger = logging.getLogger('yatuner')

        self.compiler = yatuner.Gcc(src=src,
                                    out=out,
                                    cc=cc,
                                    params_def_path=params_def_path,
                                    template=template)

        self.use_vm = use_vm
        self.cc = cc
        self.cache_dir = cache_dir

    def initialize(self):
        self.logger.info("initializing...")

        self.arch = yatuner.utils.fetch_arch()

        self.logger.info(f'arch [bold green]{self.arch}[/]')

        if yatuner.utils.execute('perf --help')['returncode'] != 0:
            self.logger.warning('perf ... [bold red]FAILD[/]')
        else:
            self.logger.info('perf ... [bold green]OK[/]')

        if yatuner.utils.execute(f'{self.cc} --help')['returncode'] != 0:
            self.logger.warning(f'{self.cc} ... [bold red]FAILD[/]')
        else:
            self.logger.info(f'{self.cc} ... [bold green]OK[/]')

        if self.use_vm:
            if self.arch == 'x86_64':
                qemu_cmd = 'qemu-x86_64'
            elif self.arch == 'arm':
                qemu_cmd = 'qemu-arm'
            else:
                qemu_cmd = ''

            if yatuner.utils.execute(f'{qemu_cmd} --help')['returncode'] != 0:
                self.logger.warning('qemu ... [bold red]FAILD[/]')
            else:
                self.logger.info('qemu ... [bold green]OK[/]')

        self.execute_cmd = self.compiler.fetch_execute_cmd()
        if self.use_vm:
            self.execute_cmd = f'{qemu_cmd} {self.execute_cmd}'

        if not os.path.exists(self.cache_dir):
            os.mkdir(self.cache_dir)

        self.optimizers = self.compiler.fetch_optimizers()
        self.parameters = self.compiler.fetch_parameters()

        self.logger.info(f"optimizers {len(self.optimizers)}")
        self.logger.info(f"parameters {len(self.parameters)}")

    def test_run(self):
        self.compiler.compile('-O3')
        self.execute_data = []

        for _ in track(range(50), description='test run'):
            time = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            self.execute_data.append(time)

        self.u = np.mean(self.execute_data)
        self.std = np.std(self.execute_data)
        kstest = stats.kstest(self.execute_data, 'norm', (self.u, self.std))

        self.logger.info(
            f"test run finished with u: {self.u:.2f}, std: {self.std:.2f}")

        if kstest.pvalue < 0.05:
            self.logger.info("test run ... [bold green]OK[/]")
        else:
            self.logger.warning(
                "[red]execution time disobey normal distribution[/]")

        plt.hist(self.execute_data, bins=50, density=True, label='test run')
        plt.legend()
        plt.savefig(self.cache_dir + "/test_run_distribution.png")

    def hypotest_optimizers(self,
                            num_samples=5,
                            z_threshold=0.05,
                            t_threshold=0.05):
        self.selected_optimizers = []

        hypotest_execute_data = []

        for i, optimizer in enumerate(self.optimizers):
            try:
                self.compiler.compile(f'-O3 {optimizer} ')
            except RuntimeError as err:
                self.logger.error(f"[red]compile error with {optimizer}[/]")
                self.logger.exception(err)
                continue

            samples = np.zeros(num_samples)
            err = False

            for j in range(num_samples):
                try:
                    t = yatuner.utils.fetch_perf_stat(
                        self.execute_cmd)['user_time:u'] / 1000
                except RuntimeError as err:
                    self.logger.error(f"[red]runtime error for {optimizer}[/]")
                    self.logger.exception(err)
                    err = True
                    break

                samples[j] = t
                hypotest_execute_data.append(t)

            if err:
                continue

            samples_mean = samples.mean()
            z = (samples_mean - self.u) / (self.std / np.sqrt(len(samples)))
            p = 2 * stats.norm.sf(abs(z))
            t = stats.ttest_1samp(samples, self.u).pvalue

            self.logger.debug(f"{i}/{len(self.optimizers)} {optimizer} "
                              f"u: {self.u:.2f} -> {samples_mean:.2f}, "
                              f"p: {p:.2f}, t: {t:.2f}")

            if (p < z_threshold or t < t_threshold) and z < 0:
                self.selected_optimizers.append(optimizer)
                self.logger.info(f"[green]{optimizer} is selected[/]")

        with open(self.cache_dir + '/selected_optimizers.txt',
                  'w',
                  encoding='utf-8') as f:
            f.writelines(
                [optimizer + '\n' for optimizer in self.selected_optimizers])

        plt.clf()
        bin_min = min(np.min(self.execute_data), np.min(hypotest_execute_data))
        bin_max = max(np.max(self.execute_data), np.max(hypotest_execute_data))
        bins = np.arange(bin_min, bin_max + 500, 500)
        plt.hist(self.execute_data, bins=bins, density=True, alpha=0.5, label='test run')
        plt.hist(hypotest_execute_data,
                 bins=bins,
                 density=True,
                 alpha=0.5,
                 label='hypotest-optimizers')
        plt.legend()
        plt.savefig(self.cache_dir + "/hypotest_optimizers_distribution.png")

    def hypotest_parameters(self, num_samples=20, t_threshold=0.05):

        if os.path.exists(self.cache_dir + '/selected_optimizers.txt'):
            self.selected_optimizers = []
            with open(self.cache_dir + '/selected_optimizers.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_optimizers = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_optimizers)} optimizers")

        options = '-O3 '
        for option in self.selected_optimizers:
            options += f'{option} '

        self.selected_parameters = []
        i = 0
        for parameter, r in self.parameters.items():
            r_min, r_max, default = r

            samples_min = np.zeros(num_samples)
            try:
                self.compiler.compile(f'{options} --param={parameter}={r_min}')
            except RuntimeError as err:
                self.logger.error(f"[red]compile error with {parameter}[/]")
                self.logger.exception(err)
                continue

            for j in range(num_samples):
                t = yatuner.utils.fetch_perf_stat(
                    self.execute_cmd)['user_time:u'] / 1000
                samples_min[j] = t

            samples_max = np.zeros(num_samples)
            try:
                self.compiler.compile(f'{options} --param={parameter}={r_max}')
            except RuntimeError as err:
                self.logger.error(f"[red]compile error with {parameter}[/]")
                self.logger.exception(err)
                continue

            for j in range(num_samples):
                t = yatuner.utils.fetch_perf_stat(
                    self.execute_cmd)['user_time:u'] / 1000
                samples_max[j] = t

            l = stats.levene(samples_min, samples_max).pvalue
            p = stats.ttest_ind(samples_min, samples_max,
                                equal_var=(l > 0.05)).pvalue

            self.logger.debug(
                f"{i}/{len(self.parameters)} {parameter} "
                f"min: {np.mean(samples_min)}, max: {np.mean(samples_max)} "
                f"l: {l:.2f}, p: {p:.2f}")

            if p < t_threshold:
                self.selected_parameters.append(parameter)
                self.logger.info(f"[green]{parameter} is selected[/]")

            i += 1

        with open(self.cache_dir + '/selected_parameters.txt',
                  'w',
                  encoding='utf-8') as f:
            f.writelines(
                [parameter + '\n' for parameter in self.selected_parameters])

    def optimize(self, num_samples=10, num_epochs=60):

        if os.path.exists(self.cache_dir + '/selected_optimizers.txt'):
            self.selected_optimizers = []
            with open(self.cache_dir + '/selected_optimizers.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_optimizers = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_optimizers)} optimizers")

        options = '-O3 '
        for option in self.selected_optimizers:
            options += f'{option} '

        try:
            self.compiler.compile(options)
        except RuntimeError as err:
            self.logger.error(f"[red]compile error[/]")
            self.logger.exception(err)
            return

        t = 0
        for _ in track(range(num_samples), "before optimization"):
            t += yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
        t /= num_samples
        self.logger.info(f"execution time before optimize: {t}")

        if os.path.exists(self.cache_dir + '/selected_parameters.txt'):
            self.selected_parameters = []
            with open(self.cache_dir + '/selected_parameters.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_parameters = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_parameters)} parameters")

        cnt = 0

        def step(vals) -> float:

            nonlocal cnt

            step_options = deepcopy(options)
            real_vals = []
            for i, parameter in enumerate(self.selected_parameters):
                v = round(vals[0][i] * (self.parameters[parameter][1] -
                                        self.parameters[parameter][0]) +
                          self.parameters[parameter][0])
                real_vals.append(v)
                step_options += f'--param={parameter}={int(v)} '

            self.compiler.compile(step_options)

            t = 0
            for _ in track(range(num_samples), f'step {cnt}'):
                t += yatuner.utils.fetch_perf_stat(
                    self.execute_cmd)['user_time:u'] / 1000
            t /= num_samples

            self.logger.debug(f'{cnt}/{num_epochs} result: {t:.2f}')

            cnt += 1

            return t

        bounds = [{
            'name': parameter,
            'type': 'continuous',
            'domain': (0, 1)
        } for parameter in self.selected_parameters]

        method = GPyOpt.methods.BayesianOptimization(step,
                                                     domain=bounds,
                                                     acquisition_type='LCB',
                                                     acquisition_weight=0.2)
        method.run_optimization(max_iter=num_epochs)
        method.plot_convergence(self.cache_dir + '/convergence.png')

        self.logger.info(f"best result: {method.fx_opt.flatten()[0]}")
        self.logger.info(f"best option: {method.x_opt}")

        vals = method.x_opt
        with open(self.cache_dir + '/optimized_parameters.txt',
                  'w',
                  encoding='utf-8') as file:

            for i, parameter in enumerate(self.selected_parameters):
                v = round(vals[i] * (self.parameters[parameter][1] -
                                     self.parameters[parameter][0]) +
                          self.parameters[parameter][0])

                file.write(f'{parameter} {int(v)}\n')

    def run(self, num_samples=20):
        samples_ofast = np.zeros(num_samples)
        samples_o0 = np.zeros(num_samples)
        samples_o1 = np.zeros(num_samples)
        samples_o2 = np.zeros(num_samples)
        samples_o3 = np.zeros(num_samples)
        samples_optimizers = np.zeros(num_samples)
        samples_parameters = np.zeros(num_samples)

        self.compiler.compile('-Ofast')
        for i in track(range(num_samples), description='-Ofast'):
            t = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            samples_ofast[i] = t

        self.compiler.compile('-O0')
        for i in track(range(num_samples), description='   -O0'):
            t = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            samples_o0[i] = t

        self.compiler.compile('-O1')
        for i in track(range(num_samples), description='   -O1'):
            t = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            samples_o1[i] = t

        self.compiler.compile('-O2')
        for i in track(range(num_samples), description='   -O2'):
            t = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            samples_o2[i] = t

        self.compiler.compile('-O3')
        for i in track(range(num_samples), description='   -O3'):
            t = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            samples_o3[i] = t

        if os.path.exists(self.cache_dir + '/selected_optimizers.txt'):
            self.selected_optimizers = []
            with open(self.cache_dir + '/selected_optimizers.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_optimizers = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_optimizers)} optimizers")
        else:
            pass

        options = '-O3 '
        for option in self.selected_optimizers:
            options += f'{option} '

        self.compiler.compile(options)
        for i in track(range(num_samples), description='optimizers'):
            t = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            samples_optimizers[i] = t

        if os.path.exists(self.cache_dir + '/optimized_parameters.txt'):
            cnt = 0
            with open(self.cache_dir + '/optimized_parameters.txt',
                      'r',
                      encoding='utf-8') as file:
                for line in file.readlines():
                    cnt += 1
                    parameter, val = line.strip().split(' ')
                    options += f'--param={parameter}={val} '

            self.logger.info(f"loaded {cnt} parameters")
        else:
            pass

        self.compiler.compile(options)
        for i in track(range(num_samples), description='parameters'):
            t = yatuner.utils.fetch_perf_stat(
                self.execute_cmd)['user_time:u'] / 1000
            samples_parameters[i] = t

        plt.clf()
        # plt.hist(samples_o0, density=True, alpha=0.5, label='O0')
        plt.hist(samples_o1, density=True, alpha=0.5, label='O1')
        plt.hist(samples_o2, density=True, alpha=0.5, label='O2')
        plt.hist(samples_o3, density=True, alpha=0.5, label='O3')
        plt.hist(samples_ofast, density=True, alpha=0.5, label='Ofast')
        plt.hist(samples_optimizers,
                 density=True,
                 alpha=0.5,
                 label='Optimizers')
        plt.hist(samples_parameters,
                 density=True,
                 alpha=0.5,
                 label='Parameters')
        plt.xlabel("Time/Tick")
        plt.ylabel("Density")
        plt.legend()
        plt.savefig(self.cache_dir + "/result.png")


if __name__ == '__main__':
    src = 'tests/src/united.cpp'
    out = 'tests/build/united.exe'
    optimizer = yatuner.optimizer.Optimizer(src=src,
                                            out=out,
                                            cc='g++',
                                            use_vm=False)
    optimizer.initialize()
    optimizer.test_run()
    optimizer.hypotest_optimizers()
    optimizer.hypotest_parameters()
    optimizer.optimize()
    optimizer.run()