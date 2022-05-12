import os
import subprocess
import platform

from yatuner.errors import CompileError


def execute(cmd):
    """Execute given command
    
    Args:
        cmd: command to be executed.
    
    """
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        print(p.communicate())
        raise CompileError()


def fetch_platform() -> str:
    """Fetch current platform

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
    """Fetch size of given file

    Args:
        path: path to the file

    Returns:
        The size of file by bytes.
    
    """

    return os.path.getsize(path)
