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