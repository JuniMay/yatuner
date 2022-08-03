from math import log10
from copy import deepcopy
from email.mime import base
import os
from typing import Callable, Dict, Mapping, Sequence, Tuple, Any

import numpy as np
import yatuner
from yatuner import LinUCB
import logging

import GPyOpt

from rich.logging import RichHandler
from rich.table import Table
from rich.console import Console
from rich.progress import track
from scipy import stats
from scipy import optimize
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd


class Tuner:

    def __init__(self,
                 call_compile: Callable[[Sequence[str], Mapping, str], None],
                 call_running: Callable[[], float],
                 optimizers: Sequence[str],
                 parameters: Mapping[str, Tuple],
                 call_perf: Callable[[], Dict[str, Any]]=None,
                 workspace='yatuner.db',
                 log_level=logging.DEBUG,
                 symmetrization=True) -> None:

        logging.basicConfig(format='[ %(name)s ] %(message)s',
                            handlers=[
                                RichHandler(level=log_level,
                                            markup=True,
                                            show_path=False)
                            ])
        self.logger = logging.getLogger('yatuner')
        self.logger.setLevel(log_level)

        self.call_compile = call_compile
        self.call_running = call_running
        self.call_perf = call_perf
        self.optimizers = optimizers
        self.parameters = parameters
        self.workspace = workspace
        self.symmetrization = symmetrization

    def initialize(self):
        if not os.path.isdir(self.workspace):
            self.logger.info("workspace is not detected, creating one.")
            os.mkdir(self.workspace)

    def test_run(self, num_samples=200, warmup=50):
        self.call_compile(None, None, None)
        self.exec_data = []

        for i in track(range(warmup), description=' warmup'):
            res = self.call_running()
            self.logger.debug(f"warmup {i}/{warmup} result: {res}")

        for _ in track(range(num_samples), description='testrun'):
            res = self.call_running()
            self.exec_data.append(res)

        if self.symmetrization:
            self.exec_data.sort()
            kernel = stats.gaussian_kde(self.exec_data)
            maxima = optimize.minimize_scalar(lambda x: -kernel(x),
                                              bounds=(np.min(self.exec_data),
                                                      np.max(self.exec_data)),
                                              method='bounded').x[0]
            data_cnt = len(self.exec_data)
            for i in range(data_cnt):
                self.exec_data.append(maxima + maxima - self.exec_data[i])
        else:
            self.exec_data = np.sort(
                self.exec_data)[:int(len(self.exec_data) * 0.8)]

        self.u = np.mean(self.exec_data)
        self.std = np.std(self.exec_data)
        kstest = stats.kstest(self.exec_data, 'norm', (self.u, self.std))

        self.logger.info(
            f"test run finished with u: {self.u:.2f}, std: {self.std:.2f}")

        if kstest.pvalue < 0.05:
            self.logger.info("test run ... [bold green]OK[/]")
        else:
            self.logger.warning(
                "[red]execution time disobey normal distribution[/]")

        plt.hist(self.exec_data, bins=50, density=True, label='test run')
        plt.legend()
        plt.savefig(self.workspace + "/test_run_distribution.png")

    def hypotest_optimizers(self,
                            num_samples=10,
                            z_threshold=0.05,
                            t_threshold=0.05):

        if os.path.exists(self.workspace + '/selected_optimizers.txt'):
            self.logger.info("using existing selected optimizers.")
            return

        self.selected_optimizers = []

        hypotest_exec_data = []

        for i, optimizer in enumerate(self.optimizers):
            try:
                self.call_compile([optimizer], None, None)
            except RuntimeError as err:
                self.logger.error(f"[red]compile error with {optimizer}[/]")
                self.logger.exception(err)
                continue

            samples = np.zeros(num_samples)
            err = False

            for j in range(num_samples):
                try:
                    res = self.call_running()
                except RuntimeError as err:
                    self.logger.error(f"[red]runtime error for {optimizer}[/]")
                    self.logger.exception(err)
                    err = True
                    break

                samples[j] = res
                hypotest_exec_data.append(res)

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

        with open(self.workspace + '/selected_optimizers.txt',
                  'w',
                  encoding='utf-8') as f:
            f.writelines(
                [optimizer + '\n' for optimizer in self.selected_optimizers])

        plt.clf()
        # bin_min = min(np.min(self.exec_data), np.min(hypotest_exec_data))
        # bin_max = max(np.max(self.exec_data), np.max(hypotest_exec_data))
        # bins = np.arange(bin_min, bin_max + 500, 500)
        plt.hist(
            self.exec_data,
            #  bins=bins,
            density=True,
            alpha=0.5,
            label='test run')
        plt.hist(
            hypotest_exec_data,
            #  bins=bins,
            density=True,
            alpha=0.5,
            label='hypotest-optimizers')
        plt.legend()
        plt.savefig(self.workspace + "/hypotest_optimizers_distribution.png")

    def hypotest_parameters(self, num_samples=10, t_threshold=0.05):

        if os.path.exists(self.workspace + '/selected_parameters.txt'):
            self.logger.info("using existing selected parameters")
            return

        if os.path.exists(self.workspace + '/selected_optimizers.txt'):
            self.selected_optimizers = []
            with open(self.workspace + '/selected_optimizers.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_optimizers = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_optimizers)} optimizers")
        else:
            self.logger.error(
                "no selected optimizers detected, "
                "please run hypothesis test for optimizers first.")
            return

        self.selected_parameters = []
        i = 0
        for parameter, r in self.parameters.items():
            r_min, r_max, default = r

            samples_min = np.zeros(num_samples)
            try:
                self.call_compile(self.selected_optimizers, {parameter: r_min},
                                  None)
            except RuntimeError as err:
                self.logger.error(f"[red]compile error with {parameter}[/]")
                self.logger.exception(err)
                continue

            for j in range(num_samples):
                res = self.call_running()
                samples_min[j] = res

            samples_max = np.zeros(num_samples)
            try:
                self.call_compile(self.selected_optimizers, {parameter: r_max},
                                  None)
            except RuntimeError as err:
                self.logger.error(f"[red]compile error with {parameter}[/]")
                self.logger.exception(err)
                continue

            for j in range(num_samples):
                res = self.call_running()
                samples_max[j] = res

            l = stats.levene(samples_min, samples_max).pvalue
            p = stats.ttest_ind(samples_min, samples_max,
                                equal_var=(l > 0.05)).pvalue

            self.logger.debug(f"{i}/{len(self.parameters)} {parameter} "
                              f"min: {np.mean(samples_min):.2f}, "
                              f"max: {np.mean(samples_max):.2f} "
                              f"l: {l:.2f}, p: {p:.2f}")

            if p < t_threshold:
                self.selected_parameters.append(parameter)
                self.logger.info(f"[green]{parameter} is selected[/]")

            i += 1

        with open(self.workspace + '/selected_parameters.txt',
                  'w',
                  encoding='utf-8') as f:
            f.writelines(
                [parameter + '\n' for parameter in self.selected_parameters])
    

    def optimize_linUCB(self, alpha=0.5, num_epochs=200, num_samples=10, num_bins=25, method='parallel', nth_choice=3) -> None:
        if self.call_perf == None:
            self.logger.error("call_perf not found")
            return

        if num_bins > num_epochs:
            self.logger.error("num_epochs needs to be larger than num_bins")
            return

        if os.path.exists(self.workspace + '/optimized_parameters.txt'):
            self.logger.info("using existing optimized parameters.")
            return

        if os.path.exists(self.workspace + '/selected_optimizers.txt'):
            self.selected_optimizers = []
            with open(self.workspace + '/selected_optimizers.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_optimizers = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_optimizers)} optimizers")

        try:
            self.call_compile(self.selected_optimizers, None, None)
        except RuntimeError as err:
            self.logger.error(f"[red]compile error[/]")
            self.logger.exception(err)
            return

        baseline = 0
        for _ in track(range(num_samples), "before optimization"):
            baseline += self.call_running()
        baseline /= num_samples
        self.logger.info(f"execution result before optimize: {baseline}")

        if os.path.exists(self.workspace + '/selected_parameters.txt'):
            self.selected_parameters = []
            with open(self.workspace + '/selected_parameters.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_parameters = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_parameters)} parameters")

        dim = len(self.call_perf())
        features = [log10(1 + x) for x in self.call_perf().values()]
        if method == 'serial':
            ucbs = [LinUCB.LinUCB(dim, 
                              np.linspace(self.parameters[param][0], self.parameters[param][1], 
                                          num_bins, 
                                          endpoint=True, 
                                          dtype='int'),
                              alpha=alpha) 
                    for param in self.selected_parameters]
            for ucb in ucbs:
                    ucb.init()
            choices = np.zeros(len(self.selected_parameters), dtype=int)
            for c in range(len(self.selected_parameters)):
                timearr = np.zeros(num_epochs)
                for i in track(range(num_epochs), description=f'optimizing parameter {c}'):
                    choices[c] = ucbs[c].recommend(features)
                    step_parameters = {}
                    for idx, param in enumerate(self.selected_parameters[:c+1]):
                        step_parameters[param] = choices[idx]
                    # print(step_parameters)
                    self.call_compile(self.selected_optimizers, step_parameters, None)
                    new_perf = self.call_perf()
                    features = [log10(1 + x) for x in new_perf.values()]
                    new_time = self.call_running() # TODO: this needs to be solved
                    reward = (baseline - new_time) / 1000
                    self.logger.info(f"r={reward} t={new_time} baseline={baseline}")
                    ucbs[c].update(reward)
                    timearr[i] = new_time
                plt.clf()
                plt.plot(timearr)
                plt.savefig(self.workspace + '/convergence_linUCB.png')
                print(choices)

        elif method == 'parallel':
            ucbs = [LinUCB.LinUCB(dim, 
                              np.linspace(self.parameters[param][0], 
                                          self.parameters[param][1], 
                                          num_bins, 
                                          endpoint=True, 
                                          dtype='int'),
                              alpha=alpha,
                              nth_choice=nth_choice) 
                    for param in self.selected_parameters]
            for ucb in ucbs:
                    ucb.init()
            choices = np.zeros(len(self.selected_parameters), dtype=int)
            timearr = np.zeros(num_epochs)
            for i in track(range(num_epochs), description='optimizing'):
                for idx, ucb in enumerate(ucbs):
                    choices[idx] = ucb.recommend(features)
                step_parameters = {}
                for idx, param in enumerate(self.selected_parameters):
                    step_parameters[param] = choices[idx]
                # print(step_parameters)
                self.call_compile(self.selected_optimizers, step_parameters, None)            
                new_perf = self.call_perf()
                features = [log10(1 + x) for x in new_perf.values()]
                new_time = self.call_running() # TODO: this needs to be solved
                reward = (baseline - new_time) / 1000
                self.logger.info(f"r={reward} t={new_time} baseline={baseline}")
                for ucb in ucbs:
                    ucb.update(reward)
                timearr[i] = new_time
            plt.clf()
            plt.plot(timearr)
            plt.savefig(self.workspace + '/convergence_linUCB.png')
            print(choices)
        else:
            self.logger.error("method needs to be either serial or parallel")
            return


        with open(self.workspace + '/optimized_parameters.txt', 'w', encoding='utf-8') as file:
            for idx, param in enumerate(self.selected_parameters):
                file.write(param + " " + str(choices[idx]) + '\n') 


    def optimize(self, num_samples=10, num_epochs=60):
        if os.path.exists(self.workspace + '/optimized_parameters.txt'):
            self.logger.info("using existing optimized parameters.")
            return

        if os.path.exists(self.workspace + '/selected_optimizers.txt'):
            self.selected_optimizers = []
            with open(self.workspace + '/selected_optimizers.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_optimizers = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_optimizers)} optimizers")

        try:
            self.call_compile(self.selected_optimizers, None, None)
        except RuntimeError as err:
            self.logger.error(f"[red]compile error[/]")
            self.logger.exception(err)
            return

        res = 0
        for _ in track(range(num_samples), "before optimization"):
            res += self.call_running()
        res /= num_samples
        self.logger.info(f"execution result before optimize: {res}")

        if os.path.exists(self.workspace + '/selected_parameters.txt'):
            self.selected_parameters = []
            with open(self.workspace + '/selected_parameters.txt',
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

            step_parameters = {}
            for i, parameter in enumerate(self.selected_parameters):
                v = round(vals[0][i] * (self.parameters[parameter][1] -
                                        self.parameters[parameter][0]) +
                          self.parameters[parameter][0])
                step_parameters[parameter] = int(v)

            self.call_compile(self.selected_optimizers, step_parameters, None)

            res = 0
            for _ in track(range(num_samples), f'step {cnt}'):
                res += self.call_running()
            res /= num_samples

            self.logger.debug(f'{cnt}/{num_epochs} result: {res:.2f}')

            cnt += 1

            return res

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
        method.plot_convergence(self.workspace + '/convergence.png')

        self.logger.info(f"best result: {method.fx_opt.flatten()[0]}")
        self.logger.info(f"best option: {method.x_opt}")

        vals = method.x_opt
        with open(self.workspace + '/optimized_parameters.txt',
                  'w',
                  encoding='utf-8') as file:

            for i, parameter in enumerate(self.selected_parameters):
                v = round(vals[i] * (self.parameters[parameter][1] -
                                     self.parameters[parameter][0]) +
                          self.parameters[parameter][0])

                file.write(f'{parameter} {int(v)}\n')

    def run(self, num_samples=10):
        samples_ofast = np.zeros(num_samples)
        samples_o0 = np.zeros(num_samples)
        samples_o1 = np.zeros(num_samples)
        samples_o2 = np.zeros(num_samples)
        samples_o3 = np.zeros(num_samples)
        samples_optimizers = np.zeros(num_samples)
        samples_parameters = np.zeros(num_samples)

        self.call_compile(None, None, '-Ofast')
        for i in track(range(num_samples), description='-Ofast'):
            res = self.call_running()
            samples_ofast[i] = res

        # self.call_compile(None, None, '-O0')
        # for i in track(range(num_samples), description='   -O0'):
        #     res = self.call_running()
        #     samples_o0[i] = t

        self.call_compile(None, None, '-O1')
        for i in track(range(num_samples), description='   -O1'):
            res = self.call_running()
            samples_o1[i] = res

        self.call_compile(None, None, '-O2')
        for i in track(range(num_samples), description='   -O2'):
            res = self.call_running()
            samples_o2[i] = res

        self.call_compile(None, None, '-O3')
        for i in track(range(num_samples), description='   -O3'):
            res = self.call_running()
            samples_o3[i] = res

        if os.path.exists(self.workspace + '/selected_optimizers.txt'):
            self.selected_optimizers = []
            with open(self.workspace + '/selected_optimizers.txt',
                      'r',
                      encoding='utf-8') as file:
                self.selected_optimizers = [
                    x.strip() for x in file.readlines()
                ]

            self.logger.info(
                f"loaded {len(self.selected_optimizers)} optimizers")
        else:
            pass

        self.call_compile(self.selected_optimizers, None, None)
        for i in track(range(num_samples), description='optimizers'):
            res = self.call_running()
            samples_optimizers[i] = res

        if os.path.exists(self.workspace + '/optimized_parameters.txt'):
            self.optimized_parameters = {}
            with open(self.workspace + '/optimized_parameters.txt',
                      'r',
                      encoding='utf-8') as file:
                for line in file.readlines():
                    parameter, val = line.strip().split(' ')
                    self.optimized_parameters[parameter] = val

            self.logger.info(
                f"loaded {len(self.optimized_parameters)} parameters")
        else:
            pass

        self.call_compile(self.selected_optimizers, self.optimized_parameters,
                          None)
        for i in track(range(num_samples), description='parameters'):
            res = self.call_running()
            samples_parameters[i] = res

        bin_min = min(np.min(samples_o1), np.min(samples_o2),
                      np.min(samples_o3), np.min(samples_ofast),
                      np.min(samples_optimizers), np.min(samples_parameters))
        bin_max = max(np.max(samples_o1), np.max(samples_o2),
                      np.max(samples_o3), np.max(samples_ofast),
                      np.max(samples_optimizers), np.max(samples_parameters))
        bins = np.arange(bin_min, bin_max + 500, 500)

        plt.clf()
        # plt.hist(samples_o0, density=True, alpha=0.5, label='O0')
        plt.hist(samples_o1, bins=bins, density=True, alpha=0.5, label='O1')
        plt.hist(samples_o2, bins=bins, density=True, alpha=0.5, label='O2')
        plt.hist(samples_o3, bins=bins, density=True, alpha=0.5, label='O3')
        plt.hist(samples_ofast,
                 bins=bins,
                 density=True,
                 alpha=0.5,
                 label='Ofast')
        plt.hist(samples_optimizers,
                 bins=bins,
                 density=True,
                 alpha=0.5,
                 label='Optimizers')
        plt.hist(samples_parameters,
                 bins=bins,
                 density=True,
                 alpha=0.5,
                 label='Parameters')
        plt.xlabel("Time/Tick")
        plt.ylabel("Density")
        plt.legend()
        plt.savefig(self.workspace + "/result.png")

        pd_data = pd.DataFrame({
            'O1': samples_o1,
            'O2': samples_o2,
            'O3': samples_o3,
            'Ofast': samples_ofast,
            'Optimizers': samples_optimizers,
            'parameters': samples_parameters
        })
        pd_data.to_csv(self.workspace + "/result.csv", index=0)

        mean_ofast = samples_ofast.mean()
        # mean_o0 = samples_o0.mean()
        mean_o1 = samples_o1.mean()
        mean_o2 = samples_o2.mean()
        mean_o3 = samples_o3.mean()
        mean_optimizers = samples_optimizers.mean()
        mean_parameters = samples_parameters.mean()

        minimal = min(mean_ofast, mean_o1, mean_o2, mean_o3, mean_optimizers,
                      mean_parameters)

        score_ofast = 100 * minimal / mean_ofast
        score_o1 = 100 * minimal / mean_o1
        score_o2 = 100 * minimal / mean_o2
        score_o3 = 100 * minimal / mean_o3
        score_optimizers = 100 * minimal / mean_optimizers
        score_parameters = 100 * minimal / mean_parameters

        delta_optimizers = (score_optimizers - score_o2) / score_o2 * 100
        delta_parameters = (score_parameters - score_o2) / score_o2 * 100

        table = Table(title="Result")
        table.add_column("Method")
        table.add_column(f"Result", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Delta", style="green")
        table.add_row("Ofast", f"{mean_ofast:.2f}", f"{score_ofast:.2f}", "")
        table.add_row("O1", f"{mean_o1:.2f}", f"{score_o1:.2f}", "")
        table.add_row("O2", f"{mean_o2:.2f}", f"{score_o2:.2f}", "")
        table.add_row("O3", f"{mean_o3:.2f}", f"{score_o3:.2f}", "")
        table.add_row("Optimizers", f"{mean_optimizers:.2f}",
                      f"{score_optimizers:.2f}", f"{delta_optimizers:.2f}%")
        table.add_row("Parameters", f"{mean_parameters:.2f}",
                      f"{score_parameters:.2f}", f"{delta_parameters:.2f}%")

        console = Console()
        console.print(table)
    
    def plot_data(self) -> None:
        if not os.path.exists(self.workspace + '/result.csv'):
            self.logger.error("No data found.")
            return
        plt.style.use('seaborn')
        pd_data = pd.read_csv(self.workspace + "/result.csv")
        plt.clf()
        sns.violinplot(data=pd_data, orient='horizontal', palette='Set2', width=0.9)
        plt.title('Time Comparison')
        plt.ylabel('Optimization_methods')
        plt.xlabel('Time/Tick - Lower the better')
        plt.grid()
        plt.savefig(self.workspace + "/result_violin.png")
