import datetime
import os


def generate(filename: str):
    file = open(filename, 'w', encoding='utf-8')

    date = datetime.date.today()

    content = f'''# -*- coding: utf-8 -*-

################################################################################
# yaTuner configuration file
# This file is auto generated by yaTuner.
# {date.year}-{date.month}-{date.day}
################################################################################

################################################################################
import logging
import yatuner
import os

build_dir = './build'  # building directory for executable file.
workspace = './workspace'  # workspace to store tuning result.

# making building directory if necessary
if not os.path.isdir(build_dir):
    os.mkdir(build_dir)

# you can replace these with auto-fetched or appointed optimizers/parameters.
optimizers = []
parameters = {{}}

################################################################################


################################################################################
# defining compiling process
def comp(optimizers, parameters, additional):
    raise NotImplementedError()


# run executable file and return a value representing its performance/size/etc.
def run():
    raise NotImplementedError()


# fetch performance counters or features of the program (for linUCB)
def perf():
    raise NotImplementedError()


# defining tuner
tuner = yatuner.Tuner(call_compile=comp,
                    call_running=run,
                    call_perf=perf,
                    optimizers=optimizers,
                    parameters=parameters,
                    workspace=workspace,
                    log_level=logging.INFO,
                    norm_range=1.0)
################################################################################


################################################################################
# tuning process
tuner.initialize()
tuner.test_run(num_samples=500, warmup=0)
tuner.hypotest_optimizers(num_samples=5)
tuner.hypotest_parameters(num_samples=5)
# tuner.optimize(num_samples=10) # using bayesian optimization
tuner.optimize_linUCB(alpha=0.25, num_bins=30, num_epochs=200,
                    nth_choice=4)  # using linUCB
tuner.run(num_samples=50)
tuner.plot_data()
################################################################################
    '''
    
    file.write(content)

    file.close()