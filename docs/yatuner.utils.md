<!-- markdownlint-disable -->

<a href="../yatuner/utils.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `yatuner.utils`





---

<a href="../yatuner/utils.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `execute`

```python
execute(command) → Dict[str, Any]
```

Execute given command. 



**Args:**
 
 - <b>`command`</b>:  Command to be executed. 


---

<a href="../yatuner/utils.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_perf_stat`

```python
fetch_perf_stat(command) → Dict[str, Any]
```

Use `perf stat <command>` to analyze given program and get dict of counters. 



**Args:**
 
 - <b>`command`</b>:  Command to be used in `perf stat`. 


---

<a href="../yatuner/utils.py#L116"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `ir2vec`

```python
ir2vec(llvm_ir, outfile, mode='fa', vocab='vocab.txt', level='p')
```

Call ir2vec tool and fetch the result. 


---

<a href="../yatuner/utils.py#L129"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `generate_llvm`

```python
generate_llvm(src, llvm_ir, llvm_compiler='clang') → None
```

Generate llvm ir for source code. 


---

<a href="../yatuner/utils.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_src_feature`

```python
fetch_src_feature(
    src: str,
    llvm_ir=None,
    outfile=None,
    clean=False
) → <built-in function array>
```

Fetch source code feature by using ir2vec. 


---

<a href="../yatuner/utils.py#L176"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_arch`

```python
fetch_arch() → str
```

Fetch machine architecture information. 



**Returns:**
 
 - <b>`str`</b>:  The architecture 


---

<a href="../yatuner/utils.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_gcc_optimizers`

```python
fetch_gcc_optimizers(cc='gcc') → List[str]
```

Fetch gcc optimizers 



**Args:**
 
 - <b>`cc`</b> (str, optional):  Specified gcc binary. Defaults to 'gcc'. 



**Returns:**
 
 - <b>`List[str]`</b>:  Optimizers 


---

<a href="../yatuner/utils.py#L203"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_gcc_version`

```python
fetch_gcc_version(cc='gcc') → Tuple[int, int, int]
```

Fetch gcc version. 



**Args:**
 
 - <b>`cc`</b> (str, optional):  Specified gcc binary. Defaults to 'gcc'. 



**Returns:**
 
 - <b>`Tuple[int, int, int]`</b>:  gcc version in triplet. 


---

<a href="../yatuner/utils.py#L221"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_gcc_parameters`

```python
fetch_gcc_parameters(
    cc='gcc',
    params_def: str = None
) → Dict[str, Tuple[int, int, int]]
```

Fetch gcc parameters and its range 



**Args:**
 
 - <b>`cc`</b> (str, optional):  Specified gcc binary. Defaults to 'gcc'. 
 - <b>`params_def`</b> (str, optional):  `params.def` of gcc source for version earlier then 10. Defaults to None. 



**Raises:**
 
 - <b>`RuntimeError`</b>:  If `params.def` is not given for gcc earlier than 10. 



**Returns:**
 
 - <b>`Dict[str, Tuple[int, int, int]]`</b>:  Parameters in format of `param: (min, max, default)`. 


---

<a href="../yatuner/utils.py#L291"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_gcc_enabled_optimizers`

```python
fetch_gcc_enabled_optimizers(cc='gcc', options='-O3') → List[str]
```

Fetch enabled optimizers of certain options 



**Args:**
 
 - <b>`cc`</b> (str, optional):  Specified gcc binary. Defaults to 'gcc'. 
 - <b>`options`</b> (str, optional):  Options to look into. Defaults to '-O3'. 



**Returns:**
 
 - <b>`List[str]`</b>:  Enabled optimizers. 


---

<a href="../yatuner/utils.py#L311"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `fetch_size`

```python
fetch_size(filename: str) → int
```

Fetch file size 



**Args:**
 
 - <b>`filename`</b> (str):  Path to file. 



**Returns:**
 
 - <b>`int`</b>:  File size in bytes. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
