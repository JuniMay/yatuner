# 用例使用解析

## polybench

### 目录结构

```
.
├── build            ---- （自动生成）子程序运行时间调优构建文件夹
├── build_size       ---- （自动生成）子程序程序体积调优构建文件夹
├── polybench        ---- polybench 项目源码
├── tune.py          ---- 定义编译过程及运行时间优化过程
├── tune_size.py     ---- 定义编译过程及程序体积优化过程
├── workspace        ---- （自动生成）各个子程序运行时间优化结果
│   ├── deriche.db
│   ├── nussinov.db
│   └── ...
└── workspace_size   ---- （自动生成）各个子程序程序体积优化结果
    ├── deriche.db
    ├── nussinov.db
    └── ...
```

## matmul, raytracer, tsp-ga

此三者用例来自 Opentuner 有关 gcc 的示例。

### 目录结构

```
├── build            ---- （自动生成）项目构建文件夹
├── src              ---- 源码文件夹
├── tune.py          ---- 定义编译过程及运行时间优化过程
├── yatuner.db       ---- （自动生成）运行时间调优结果
```

## triple

此用例源码基于 Opentuner 有关 gcc 例子进行编写，将 `raytracer`, `tsp-ga` 和 `matmul` 结合了起来。

### 目录结构

```
├── build            ---- （自动生成）项目构建文件夹
├── src
│   └── triple.cpp   ---- 源码
├── tune.py          ---- 定义编译过程及运行时间优化过程
├── tune_size.py     ---- 定义编译过程及程序体积优化过程
├── yatuner.db       ---- （自动生成）运行时间调优结果
└── yatuner_size.db  ---- （自动生成）程序体积调优结果
```