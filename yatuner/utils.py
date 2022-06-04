import os
import subprocess
import platform

import yatuner
import time


def execute(cmd) -> None:
    """Execute given command.
    
    Args:
        cmd: command to be executed.

    Raises:
        CompileError: if command return code is not 0.
    
    """
    with subprocess.Popen(cmd,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as p:
        stdout = p.communicate()

        if p.returncode != 0:
            print(f"Error occured while executing {cmd}")
            print(f"Return code: {p.returncode}")
            print(f"Message: {stdout[1].decode('GBK')}")
            p.terminate()
            raise yatuner.errors.ExecuteError()

        p.terminate()


def timing(cmd) -> float:
    """Execute a command and timing

    Args:
        cmd: command to be executed.

    Returns:
        time consumed in ms
    
    """

    with subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE) as p:
        t_st = time.perf_counter()
        stdout = p.communicate()
        t_ed = time.perf_counter()
        if p.returncode != 0:
            print(f"Error occured while executing {cmd}")
            print(f"Return code: {p.returncode}")
            print(f"Message: {stdout[1]}")
            p.terminate()
            return float('inf')
        p.terminate()

    return (t_ed - t_st) * 1000


def fetch_platform() -> str:
    """Fetch current platform.

    Returns:
        A string indication platform.
    
    """

    p = platform.platform().upper()

    if 'LINUX' in p:
        return 'LINUX'
    elif 'WINDOWS' in p:
        return 'WINDOWS'
    else:
        return 'UNKNOWN'


def fetch_file_size(path) -> int:
    """Fetch size of given file.

    Args:
        path: path to the file

    Returns:
        The size of file by bytes.
    
    """

    return os.path.getsize(path)


def get_executable(filename) -> str:
    """

    Args:
        filename: filename to execute

    Returns:
        cmd executable filename

    """

    if fetch_platform() == 'WINDOWS':
        return filename.replace('/', '\\') + '.exe'
    else:
        return filename
