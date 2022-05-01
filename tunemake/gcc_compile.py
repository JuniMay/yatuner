import os
from typing import List

def gcc_compile(infile: str,
                outfile: str,
                stage: str = None,
                std: str = None,
                gprof: bool = False,
                optimize: str = None,
                warn_list: List[str] = [],
                option_list: List[str] = [],
                machine_option_list: List[str] = [],
                include_dir_list: List[str] = [],
                lib_dir_list: List[str] = []) -> None:
    """Run gcc command with given options.

    This function will not check the validity of given arguments.
    
    Args:
        infile: path to file to be compiled.
        outfile: path to output file.
        stage: compilation stage, among `c`, `S`, `E` or None.
        std: standard.
        gprof: enable gprof if `True`.
        optimize: optimize level in gcc.
        warn_list: options for `-W`
        option_list: options for `-f`
        machine_option_list: options for `-m`
        include_dir_list: options for `-I`
        lib_dir_list: options for `-L`

    """
    command: str = 'gcc'

    if stage:
        if stage in ['c', 'S', 'E']:
            command += f' -{stage}'
        else:
            pass
    
    if std:
        command += f' -std={std}'

    if gprof:
        command += ' -pg'

    if optimize:
        command += f' -O{optimize}'

    for warn in warn_list:
        command += f' -W{warn}'

    for include_dir in include_dir_list:
        command += f' -I{include_dir}'

    for lib_dir in lib_dir_list:
        command += f' -L{lib_dir}'

    for option in option_list:
        command += f' -f{option}'

    for machine_option in machine_option_list:
        command += f' -m{machine_option}'

    command += f' -o {outfile} {infile}'

    os.system(command)


    




    