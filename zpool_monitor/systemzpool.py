"""
This module implements a set of functions to run the zpool command and return the output as a dictionary that can be used.

On first import we will try to locate the zpool command and raise an exception if it is not found on the system.
"""

# Import System Libraries
from typing import Any
import shutil
import subprocess
import json


"""
Find the zpool binary during importing
"""
_zpool_binary: str | None = shutil.which("zpool")
if not _zpool_binary: raise FileNotFoundError('Executable ([green]zpool[/]) executable not found on system')


def _run_zpool_binary(command: str, params: list[str]) -> dict[str, Any]:
    """
    Run the zpool program with the nominated command and parameters. We always run zpool to output in JSON format and convert to a dictionary to return.

    :param command: The zpool sub-command to execute.
    :param params: Extra parameters to pass to the zpool sub-command.
    :return: JSON Output is converted to a dictionary, and the 'pools' key is returned.
    """
    return json.loads(subprocess.run([_zpool_binary, command, '-j', '--json-int'] + params, capture_output=True, text=True).stdout)['pools']


def get_zpools() -> list[str]:
    """
    Run 'zpool list' to obtain a list of all available ZPools on the system to return.

    :return: List of available ZPools
    """
    return list(_run_zpool_binary(command='list', params=['-H', '-o', 'name']).keys())


def get_zpools_status(poolnames: list[str]) -> dict[str, Any]:
    """
    Run 'zpool status' to obtain the current status of the nominated zpools as a dict

    :param poolnames: List of selected ZPool names to retrieve status for. An empty list means all pools are retrieved.
    :return: Dictionary mapping pool name to status for that pool as a dictionary
    """
    return dict(_run_zpool_binary(command='status', params=['-t'] + poolnames).items())
