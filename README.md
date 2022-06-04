# proj105-yaTuner: 编译器自动调优

## 设计目标

针对多目标（代码大小、运行速度、内存占用等）实现对 GCC 优化选项、链接库选项的自动调参。

## 前期调研

针对 GCC 编译和程序运行参数离散，目标函数导数未知等特征，调研超参数优化问题的常见解决方法，选择使用启发式搜索算法对参数进行搜索，同时根据程序 Profiling 结果进一步优化参数。

## 当前开发状况

- [x] GCC 调用封装
- [x] 对代码大小优化：能够得到相比 `-Os` 较小的程序
- [x] 对运行速度优化：目前在某些程序上能够得到比 `-O3` 或 `-O2` 更好的效果
- [x] 贝叶斯优化方法
- [ ] openEular环境适配
- [ ] 优化目标配置文件
- [ ] 对内存占用优化
- [ ] 测试其他优化方式（遗传算法等）
- [ ] 对编译错误和警告的处理
- [ ] Topdown 分析
- [ ] Profiling-based 优化
- [ ] 针对带参数的编译选项的优化

## 沟通情况

已与导师建立有效的沟通渠道。

## 当前困难

- 对代码进行编译运行的时间可能较长，对优化的速度有影响，目前想通过批处理的方式进行优化
- 运行时间优化方面存在计时不准的问题（考虑使用 profiling 程序进行）
- 运行时间优化耗时太长，且效果不佳/不稳定（考虑在 `-O2` 的基础上进行进一步调优）

## 使用示例

### 体积优化示例 —— 以 polybench 中的程序为例

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

### 速度优化示例

```python

gcc = yatuner.compilers.Gcc(infiles=['tests/samples/euler.c'],
                            outfile='tests/build/euler')
# 指定优化目标为运行时间
optimizer = yatuner.optimizers.BayesianOptimizer(gcc, goal='time') 
optimizer.optimize(10)
```