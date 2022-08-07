# 用例使用解析

## polybench

### 目录结构

```
.
├── build            ---- 子程序构建文件夹
├── polybench        ---- polybench 项目源码
├── README.md
├── tune.py          ---- 定义编译过程及优化过程
└── workspace        ---- 各个子程序优化结果
    ├── deriche.db
    ├── nussinov.db
    └── ...
```

## triple

此用例源码基于 openTuner 有关 gcc 例子进行编写，将 `raytracer`, `tsp-ga` 和 `matmul` 结合了起来。

### 目录结构

```
├── build           ---- 项目构建文件夹
├── README.md
├── src
│   └── triple.cpp  ---- 源码
├── tune.py         ---- 定义编译过程及优化过程
└── yatuner.db      ---- 调优结果
```