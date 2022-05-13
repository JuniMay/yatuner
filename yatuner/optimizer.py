import GPyOpt
from typing import List
from abc import abstractmethod


class Optimizer(object):
    @abstractmethod
    def optimize():
        raise NotImplementedError()

    @abstractmethod
    def dump():
        raise NotImplementedError()


class BayesianOptimizer(Optimizer):
    def __init__(self, compiler, goal: str = 'size'):
        self.goal = goal
        self.compiler = compiler

        if self.goal == 'size':
            pass
        elif self.goal == 'speed':
            pass
        else:
            pass

    def step(self, options: List[List[int]]) -> int:
        if (self.goal == 'size'):
            self.compiler.execute(options[0])

        size = self.compiler.fetch_size()
        print(size)
        return size

    def optimize(self, epochs=50) -> None:

        bounds = [{
            'name': 'var',
            'type': 'discrete',
            'domain': (0, 1),
            'dimensionality': len(self.compiler.option_collection)
        }]
        opt = GPyOpt.methods.BayesianOptimization(self.step,
                                                  domain=bounds,
                                                  model_type='sparseGP',
                                                  acquisition_type='EI')
        opt.run_optimization(epochs)
        opt.plot_convergence()

    def dump():
        pass