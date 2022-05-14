import os
import subprocess
import platform

import yatuner


def execute(cmd) -> None:
    """Execute given command.
    
    Args:
        cmd: command to be executed.

    Raises:
        CompileError: if command return code is not 0.
    
    """
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        p.wait()

        if p.returncode != 0:
            print(f"Error occured while executing {cmd}")
            print(f"Return code: {p.returncode}")
            print(f"Message: {p.communicate()}")
            p.terminate()
            raise yatuner.errors.ExecuteError()

        p.terminate()


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
