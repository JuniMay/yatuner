from typing import List
from abc import abstractmethod

import yatuner


class Compiler(object):
    @abstractmethod
    def execute(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def fetch_size(self) -> int:
        raise NotImplementedError()


class Gcc(Compiler):
    """Just Gcc.
    
    Attributes:
        stage: stage of compilation, e.g. `E`, `S`, `c`.
        infiles: list of input files.
        outfile: path to output file.
        warnings: `-W` options, prefix will be added.
        libs: path to libraries.
        incs: path to headers.
        lib_dirs: directories for libraries.
        inc_dirs: directories for headers.
        adds: in case of other options.

    """

    option_collections = [
        'aggressive-loop-optimizations',
        # 'align-functions[=n[:m:[n2[:m2]]]]',
        # 'align-jumps[=n[:m:[n2[:m2]]]]',
        # 'align-labels[=n[:m:[n2[:m2]]]]',
        # 'align-loops[=n[:m:[n2[:m2]]]]',
        'associative-math',
        # 'auto-profile',
        # 'auto-profile[=path]',
        'auto-inc-dec',
        'branch-probabilities',
        'branch-target-load-optimize',
        'branch-target-load-optimize2',
        'btr-bb-exclusive',
        'caller-saves',
        'combine-stack-adjustments',
        'conserve-stack',
        'compare-elim',
        'cprop-registers',
        'crossjumping',
        'cse-follow-jumps',
        'cse-skip-blocks',
        'cx-fortran-rules',
        'cx-limited-range',
        'data-sections',
        'dce',
        # 'delayed-branch',
        'delete-null-pointer-checks',
        'devirtualize',
        'devirtualize-speculatively',
        'devirtualize-at-ltrans',
        'dse',
        'early-inlining',
        'ipa-sra',
        'expensive-optimizations',
        'fat-lto-objects',
        'fast-math',
        'finite-math-only',
        'float-store',
        # 'excess-precision=style',
        'forward-propagate',
        # 'fp-contract=style',
        'function-sections',
        'gcse',
        'gcse-after-reload',
        'gcse-las',
        'gcse-lm',
        'graphite-identity',
        'gcse-sm',
        'hoist-adjacent-loads',
        'if-conversion',
        'if-conversion2',
        'indirect-inlining',
        'inline-functions',
        'inline-functions-called-once',
        # 'inline-limit=n',
        'inline-small-functions',
        'ipa-cp',
        'ipa-cp-clone',
        'ipa-bit-cp',
        'ipa-vrp',
        'ipa-pta',
        # 'ipa-profile',
        # 'ipa-pure-const',
        'ipa-reference',
        'ipa-reference-addressable',
        'ipa-stack-alignment',
        'ipa-icf',
        # 'ira-algorithm=algorithm',
        # 'live-patching=level',
        # 'ira-region=region',
        'ira-hoist-pressure',
        'ira-loop-pressure',
        'no-ira-share-save-slots',
        'no-ira-share-spill-slots',
        'isolate-erroneous-paths-dereference',
        'isolate-erroneous-paths-attribute',
        'ivopts',
        'keep-inline-functions',
        'keep-static-functions',
        'keep-static-consts',
        'limit-function-alignment',
        'live-range-shrinkage',
        'loop-block',
        'loop-interchange',
        'loop-strip-mine',
        'loop-unroll-and-jam',
        'loop-nest-optimize',
        'loop-parallelize-all',
        'lra-remat',
        'lto',
        # 'lto-compression-level',
        # 'lto-partition=alg',
        'merge-all-constants',
        'merge-constants',
        'modulo-sched',
        'modulo-sched-allow-regmoves',
        'move-loop-invariants',
        'no-branch-count-reg',
        'no-defer-pop',
        'no-fp-int-builtin-inexact',
        'no-function-cse',
        'no-guess-branch-probability',
        'no-inline',
        'no-math-errno',
        'no-peephole',
        'no-peephole2',
        'no-printf-return-value',
        'no-sched-interblock',
        'no-sched-spec',
        'no-signed-zeros',
        'no-toplevel-reorder',
        'no-trapping-math',
        'no-zero-initialized-in-bss',
        'omit-frame-pointer',
        'optimize-sibling-calls',
        'partial-inlining',
        'peel-loops',
        'predictive-commoning',
        'prefetch-loop-arrays',
        # 'profile-correction',
        # 'profile-use',
        # 'profile-use=path',
        # 'profile-values',
        # 'profile-reorder-functions',
        'reciprocal-math',
        'ree',
        'rename-registers',
        'reorder-blocks',
        # 'reorder-blocks-algorithm=algorithm',
        'reorder-blocks-and-partition',
        'reorder-functions',
        'rerun-cse-after-loop',
        'reschedule-modulo-scheduled-loops',
        'rounding-math',
        'save-optimization-record',
        'sched2-use-superblocks',
        'sched-pressure',
        'sched-spec-load',
        'sched-spec-load-dangerous',
        # 'sched-stalled-insns-dep[=n]',
        # 'sched-stalled-insns[=n]',
        'sched-group-heuristic',
        'sched-critical-path-heuristic',
        'sched-spec-insn-heuristic',
        'sched-rank-heuristic',
        'sched-last-insn-heuristic',
        'sched-dep-count-heuristic',
        'schedule-fusion',
        'schedule-insns',
        'schedule-insns2',
        # 'section-anchors',
        'selective-scheduling',
        'selective-scheduling2',
        'sel-sched-pipelining',
        'sel-sched-pipelining-outer-loops',
        'semantic-interposition',
        'shrink-wrap',
        'shrink-wrap-separate',
        'signaling-nans',
        'single-precision-constant',
        'split-ivs-in-unroller',
        'split-loops',
        'split-paths',
        'split-wide-types',
        'ssa-backprop',
        'ssa-phiopt',
        'stdarg-opt',
        'store-merging',
        'strict-aliasing',
        'thread-jumps',
        'tracer',
        'tree-bit-ccp',
        'tree-builtin-call-dce',
        'tree-ccp',
        'tree-ch',
        'tree-coalesce-vars',
        'tree-copy-prop',
        'tree-dce',
        'tree-dominator-opts',
        'tree-dse',
        'tree-forwprop',
        'tree-fre',
        'code-hoisting',
        'tree-loop-if-convert',
        'tree-loop-im',
        'tree-phiprop',
        'tree-loop-distribution',
        'tree-loop-distribute-patterns',
        'tree-loop-ivcanon',
        'tree-loop-linear',
        'tree-loop-optimize',
        'tree-loop-vectorize',
        # 'tree-parallelize-loops=n',
        'tree-pre',
        'tree-partial-pre',
        'tree-pta',
        'tree-reassoc',
        'tree-scev-cprop',
        'tree-sink',
        'tree-slsr',
        'tree-sra',
        'tree-switch-conversion',
        'tree-tail-merge',
        'tree-ter',
        'tree-vectorize',
        'tree-vrp',
        'unconstrained-commons',
        'unit-at-a-time',
        'unroll-all-loops',
        'unroll-loops',
        'unsafe-math-optimizations',
        'unswitch-loops',
        'ipa-ra',
        'variable-expansion-in-unroller',
        'vect-cost-model',
        'vpt',
        'web',
        'whole-program',
        # 'wpa',
        'use-linker-plugin',
    ]
    option_windows = [
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
        'handle-exceptions',
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
        self.error = False

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
            self.cmd += f' {adds}'

    def execute(self, flag: List[int] = []) -> None:
        """Compile infiles by given flag

        Args:
            flag: option will be enabled if 
                corresponding position of `flag` is 1.
        
        """

        # TODO: options with parameters

        cmd = self.cmd

        for i in range(len(flag)):
            if flag[i] == 1:
                if yatuner.utils.fetch_platform() == 'WINDOWS':
                    cmd += f' -f{self.option_windows[i]}'
                else:
                    cmd += f' -f{self.option_collections[i]}'
            elif flag[i] > 1:
                pass  # parameter

        for self.infile in self.infiles:
            cmd += f' {self.infile}'

        if self.outfile is not None:
            cmd += f' -o {self.outfile}'

        # print(cmd)
        try:
            yatuner.utils.execute(cmd)
        except yatuner.errors.ExecuteError:
            self.error = True
        else:
            self.error = False



    def fetch_size(self) -> int:
        """Fetch file size of output file.

        Returns:
            The size of output file by bytes.
        
        """
        if self.error is True:
            return float('inf')

        if yatuner.utils.fetch_platform() == 'WINDOWS':
            return yatuner.utils.fetch_file_size(
                self.outfile.replace('/', '\\') + '.exe')
        else:
            return yatuner.utils.fetch_file_size(self.outfile)
