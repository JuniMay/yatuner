# yaTuner: 编译器自动调优
## 设计目标

针对多目标（代码大小、运行速度、内存占用等）实现对 GCC 优化选项、链接库选项的自动调参。

## 前期调研

针对 GCC 编译和程序运行参数离散，目标函数导数未知等特征，调研超参数优化问题的常见解决方法，选择使用启发式搜索算法对参数进行搜索，同时根据程序 Profiling 结果进一步优化参数。

## 当前开发状况

 - [x] GCC调用封装
 - [x] 对代码大小优化
 - [ ] 对运行速度优化
 - [ ] 对内存占用优化
 - [x] 贝叶斯优化
 - [ ] 遗传算法
 - [ ] 测试其他算法
 - [x] OpenEular环境适配
 - [ ] Topdown分析
 - [ ] Profiling-based 优化
 - [ ] 针对带参数的编译选项的优化

## 沟通情况

已与导师建立有效的沟通渠道。

## 当前困难

 - 目前暂时还无法使用测试用环境的远程服务器，仍然在在本地 Windows 及 Ubuntu 等系统上进行开发测试
 - 对代码进行编译运行的时间可能较长，对优化的速度有影响，目前想通过批处理的方式进行优化

## 使用示例

```python

from yatuner import compilers
from yatuner import optimizers

compilers.Gcc(
    stage='c',
    infiles=['tests/benchmarks/polybench/utilities/polybench.c'],
    outfile='tests/build/polybench.o',
    inc_dirs=['tests/benchmarks/polybench/utilities']).execute()

gcc = compilers.Gcc(
    infiles=[
        'tests/build/polybench.o',
        'tests/benchmarks/polybench/linear-algebra/kernels/3mm/3mm.c'
    ],
    outfile='tests/build/3mm',
    inc_dirs=[
        'tests/benchmarks/polybench/utilities',
        'tests/benchmarks/polybench/linear-algebra/kernels/3mm'
    ])

optimizer = optimizers.BayesianOptimizer(gcc)
# 执行优化，将会输出优化后的文件大小和编译命令
optimizer.optimize(15)

```