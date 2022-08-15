<!-- markdownlint-disable -->

<a href="../yatuner/tuner.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `yatuner.tuner`

**Global Variables**
---------------

- **inf**

---

<a href="../yatuner/tuner.py#L36"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Tuner`

<a href="../yatuner/tuner.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    call_compile: Callable[[Sequence[str], Mapping, str], NoneType],
    call_running: Callable[[], float],
    optimizers: Sequence[str],
    parameters: Mapping[str, Tuple],
    call_perf: Callable[[], Dict[str, Any]] = None,
    workspace='yatuner.db',
    log_level=10,
    norm_range=None,
    deterministic=False
) → None
```

A tuner. 

**Args:**

- <b>`call_compile`</b> ((Sequence[str], Mapping, str) -> None):  A function runing compilation process. 
- <b>`call_running`</b> (() -> float):  A function fetching result of target program. 
- <b>`optimizers`</b> (Sequence[str]):  List of on/of options. 
- <b>`parameters`</b> (Mapping[str, Tuple]):  List of parameters, in format of `param: (min, max, default)` 
- <b>`call_perf`</b> (() -> Dict[str, Any], optional):  Fectch feature of given program, used in linUCB. Defaults to None. 
- <b>`workspace`</b> (str, optional):  Directory to store output files. Defaults to 'yatuner.db'. 
- <b>`log_level`</b> (optional):  Log level. Defaults to logging.DEBUG. 
- <b>`norm_range`</b> (float, optional):  Cut the data of test run to get more accurate result, None if doing a symmetrization. Defaults to None. 
- <b>`deterministic`</b> (bool):  False if the result of `call_compile` is random to a certain extent, otherwise True. Defaults to False. 

---

<a href="../yatuner/tuner.py#L165"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `hypotest_optimizers`

```python
hypotest_optimizers(
    num_samples=10,
    z_threshold=0.05,
    t_threshold=0.05,
    num_epochs=30
)
```

Hypothesis test for on/of options. 

**Args:**

- <b>`num_samples`</b> (int, optional):  Sampling times for each option. Defaults to 10. 
- <b>`z_threshold`</b> (float, optional):  Z threshold. Defaults to 0.05. 
- <b>`t_threshold`</b> (float, optional):  T threshold. Defaults to 0.05. 
- <b>`num_epochs`</b> (int, optional):  optimization epoches after selection. Defaults to 30. 

---

<a href="../yatuner/tuner.py#L335"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `hypotest_parameters`

```python
hypotest_parameters(num_samples=10, t_threshold=0.05)
```

Hypothesis test for parameters. 

**Args:**

- <b>`num_samples`</b> (int, optional):  Sampling times for each parameter. Defaults to 10. 
- <b>`t_threshold`</b> (float, optional):  T threshold. Defaults to 0.05. 

---

<a href="../yatuner/tuner.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `initialize`

```python
initialize()
```

---

<a href="../yatuner/tuner.py#L564"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `optimize`

```python
optimize(num_samples=10, num_epochs=60) → None
```

Optimize selected parameters with bayesian. 

---

<a href="../yatuner/tuner.py#L443"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `optimize_linUCB`

```python
optimize_linUCB(
    alpha=0.5,
    num_epochs=200,
    num_samples=10,
    num_bins=25,
    nth_choice=3,
    metric='cpu-cycles'
) → None
```

Optimize selected parameters with linUCB. 

---

<a href="../yatuner/tuner.py#L919"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `plot_data`

```python
plot_data() → None
```

Plot result in violin graph. 

---

<a href="../yatuner/tuner.py#L680"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `run`

```python
run(num_samples=10)
```

Run result and existing options to compare. 

**Args:**

- <b>`num_samples`</b> (int, optional):  Sampling times. Defaults to 10. 

---

<a href="../yatuner/tuner.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `test_run`

```python
test_run(num_samples=200, warmup=50)
```

Doing a test run with no options indicated. 

**Args:**

- <b>`num_samples`</b> (int, optional):  Times to run. Defaults to 200. 
- <b>`warmup`</b> (int, optional):  Times to warmup. Defaults to 50. 

---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
