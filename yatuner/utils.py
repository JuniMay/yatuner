import os
import subprocess
import platform

from yatuner.errors import CompileError


def execute(cmd) -> None:
    """Execute given command
    
    Args:
        cmd: command to be executed.
    
    """
    # p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    p = subprocess.Popen(cmd,
                        shell=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    p.wait()
    # if p.returncode != 0:
    #     print(cmd)
    #     print(p.communicate())
    #     p.terminate()
    #     raise CompileError()

    p.terminate()


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
