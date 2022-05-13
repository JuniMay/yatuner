from typing import List
from abc import abstractmethod

import yatuner


class Compiler(object):
    @abstractmethod
    def execute(self):
        raise NotImplementedError()


class Gcc(Compiler):
    """Just Gcc.
    
    Attributes:
        stage: str = '',
        infiles: List[str] = [],
        outfile: str = None,
        warnings: `-W` options, prefix will be added.
        libs: path to libraries.
        incs: path to headers.
        lib_dirs: directories for libraries.
        inc_dirs: directories for headers.
        adds: in case of other options.

    """

    option_collection = [
        'aggressive-loop-optimizations',
        'align-functions',
        'align-jumps',
        'align-labels',
        'align-loops',
        'associative-math',
        'asynchronous-unwind-tables',
        'auto-inc-dec',
        'branch-count-reg',
        'branch-probabilities',
        'branch-target-load-optimize',
        'btr-bb-exclusive',
        'caller-saves',
        'code-hoisting',
        'combine-stack-adjustments',
        'compare-elim',
        'conserve-stack',
        'cprop-registers',
        'crossjumping',
        'cse-follow-jumps',
        'cx-fortran-rules',
        'cx-limited-range',
        'dce',
        'defer-pop',
        'delayed-branch',
        'delete-dead-exceptions',
        'delete-null-pointer-checks',
        'devirtualize',
        'devirtualize-speculatively',
        'dse',
        'early-inlining',
        'exceptions',
        'expensive-optimizations',
        'fast-math',
        'finite-math-only',
        'float-store',
        'forward-propagate',
        'fp-int-builtin-inexact',
        'function-cse',
        'gcse',
        'gcse-after-reload',
        'gcse-las',
        'gcse-lm',
        'gcse-sm',
        'graphite',
        'graphite-identity',
        'guess-branch-probability',
        # 'handle-exceptions',
        'exceptions',
        'hoist-adjacent-loads',
        'if-conversion',
        'indirect-inlining',
        'inline',
        'inline-atomics',
        'inline-functions',
        'inline-functions-called-once',
        'inline-small-functions',
        'ipa-bit-cp',
        'ipa-cp',
        'ipa-cp-clone',
        'ipa-icf',
        'ipa-icf-functions',
        'ipa-icf-variables',
        'ipa-profile',
        'ipa-pta',
        'ipa-pure-const',
        'ipa-ra',
        'ipa-reference',
        'ipa-sra',
        'ipa-vrp',
        'ira-hoist-pressure',
        'ira-loop-pressure',
        'ira-share-save-slots',
        'ira-share-spill-slots',
        'isolate-erroneous-paths-attribute',
        'isolate-erroneous-paths-dereference',
        'ivopts',
        'jump-tables',
        'keep-gc-roots-live',
        'lifetime-dse',
        'limit-function-alignment',
        'live-range-shrinkage',
        'loop-interchange',
        'loop-nest-optimize',
        'loop-parallelize-all',
        'loop-unroll-and-jam',
        'lra-remat',
        'math-errno',
        'modulo-sched',
        'modulo-sched-allow-regmoves',
        'move-loop-invariants',
        'non-call-exceptions',
        'nothrow-opt',
        'omit-frame-pointer',
        'opt-info',
        'optimize-sibling-calls',
        'optimize-strlen',
        'pack-struct',
        'partial-inlining',
        'peel-loops',
        'peephole',
        'plt',
        'predictive-commoning',
        'prefetch-loop-arrays',
        'printf-return-value',
        'reciprocal-math',
        'associative-math',
        'reg-struct-return',
        'rename-registers',
        'reorder-blocks',
        'reorder-blocks-and-partition',
        'reorder-functions',
        'rerun-cse-after-loop',
        'reschedule-modulo-scheduled-loops',
        'rounding-math',
        'rtti',
        'sched-critical-path-heuristic',
        'sched-dep-count-heuristic',
        'sched-group-heuristic',
        'sched-interblock',
        'sched-last-insn-heuristic',
        'sched-pressure',
        'sched-rank-heuristic',
        'sched-spec',
        'sched-spec-insn-heuristic',
        'sched-spec-load',
        'sched-spec-load-dangerous',
        'sched-stalled-insns',
        'sched-stalled-insns-dep',
        'sched2-use-superblocks',
        'schedule-fusion',
        'schedule-insns',
        'section-anchors',
        'sel-sched-pipelining',
        'sel-sched-pipelining-outer-loops',
        'sel-sched-reschedule-pipelined',
        'selective-scheduling',
        'set-stack-executable',
        'short-enums',
        'short-wchar',
        'shrink-wrap',
        'shrink-wrap-separate',
        'signaling-nans',
        'signed-zeros',
        'single-precision-constant',
        'split-ivs-in-unroller',
        'split-loops',
        'split-paths',
        'split-wide-types',
        'ssa-backprop',
        'ssa-phiopt',
        'stack-clash-protection',
        'stack-protector',
        'stack-protector-all',
        'stack-protector-explicit',
        'stack-protector-strong',
        'stdarg-opt',
        'store-merging',
        'strict-aliasing',
        'strict-enums',
        'strict-volatile-bitfields',
        'thread-jumps',
        'no-threadsafe-statics',
        'tracer',
        'trapping-math',
        'trapv',
        'tree-bit-ccp',
        'tree-builtin-call-dce',
        'tree-ccp',
        'tree-ch',
        'tree-coalesce-vars',
        'tree-copy-prop',
        'tree-cselim',
        'tree-dce',
        'tree-dominator-opts',
        'tree-dse',
        'tree-forwprop',
        'tree-fre',
        'tree-loop-distribute-patterns',
        'tree-loop-distribution',
        'tree-loop-if-convert',
        'tree-loop-im',
        'tree-loop-ivcanon',
        'tree-loop-optimize',
        'tree-loop-vectorize',
        'tree-lrs',
        'tree-partial-pre',
        'tree-phiprop',
        'tree-pre',
        'tree-pta',
        'tree-reassoc',
        'tree-scev-cprop',
        'tree-sink',
        'tree-slp-vectorize',
        'tree-slsr',
        'tree-sra',
        'tree-switch-conversion',
        'tree-tail-merge',
        'tree-ter',
        'tree-vectorize',
        'tree-vrp',
        'unconstrained-commons',
        'unroll-all-loops',
        'unroll-loops',
        'unsafe-math-optimizations',
        'unswitch-loops',
        'unwind-tables',
        'var-tracking',
        'var-tracking-assignments',
        'var-tracking-assignments-toggle',
        'var-tracking-uninit',
        'variable-expansion-in-unroller',
        'vpt',
        'web',
        'wrapv',
        'wrapv-pointer',
    ]

    def __init__(self,
                 stage: str = '',
                 infiles: List[str] = [],
                 outfile: str = None,
                 warnings: List[str] = [],
                 libs: List[str] = [],
                 incs: List[str] = [],
                 lib_dirs: List[str] = [],
                 inc_dirs: List[str] = [],
                 adds: str = None) -> None:
        self.cmd = 'gcc'

        self.stage = stage
        self.infiles = infiles
        self.outfile = outfile
        self.warnings = warnings
        self.libs = libs
        self.incs = incs
        self.lib_dirs = lib_dirs
        self.inc_dirs = inc_dirs
        self.adds = adds

        if stage not in ['', 'c', 'E', 'S']:
            raise yatuner.errors.InvalidOption()
        elif stage != '':
            self.cmd += f' -{stage}'

        for lib in libs:
            self.cmd += f' -l {lib}'

        for inc in incs:
            self.cmd += f' -i {inc}'

        for lib_dir in lib_dirs:
            self.cmd += f' -L {lib_dir}'

        for inc_dir in inc_dirs:
            self.cmd += f' -I {inc_dir}'

        if adds is not None:
            self.cmf += f' {adds}'

    def execute(self, flag: List[int] = []) -> None:

        cmd = self.cmd

        for i in range(len(flag)):
            if flag[i] == 1:
                cmd += f' -f{self.option_collection[i]}'
            elif flag[i] > 1:
                pass  # parameter

        for self.infile in self.infiles:
            cmd += f' {self.infile}'

        if self.outfile is not None:
            cmd += f' -o {self.outfile}'

        # print(cmd)
        yatuner.utils.execute(cmd)

    def fetch_size(self) -> int:
        if yatuner.utils.fetch_platform() == 'WINDOWS':
            return yatuner.utils.fetch_file_size(
                self.outfile.replace('/', '\\') + '.exe')
        else:
            return yatuner.utils.fetch_file_size(self.outfile)
