"""
This module provides the Monitor class which can track multiple ZPools and output their status for display.
"""
# Import System Libraries
import argparse
import subprocess
import json
import textwrap
import rich.console

# Import zpool.ZPool class
from . import ValidPool, ValidTheme
from .zpool import ZPool


class Monitor:
    def __init__(self, poolnames: list[str]):
        """
        Construct instance of class to monitor multipl ZPool instances

        :param poolnames: List of selected ZPool names to monitor. An empty list means all pools are monitored.
        """
        self.__poolnames = poolnames

        # List containing statistics for all pools scanned
        self.__pools: dict[str, ZPool] = {}

    def refresh_stats(self) -> dict[str, ZPool]:
        """
        Refresh the data stored in self.__pools by running 'zpool status' and parsing the output
        """
        # Import output of 'zpool status -t -j' for all nominated pools into a string
        result = subprocess.run(['zpool', 'status', '-t', '-j', '--json-int'] + self.__poolnames, capture_output=True, text=True, check=True)

        # Output is in JSON format, the 'pools' key is a dictionary mapping pool names to pool data for all scanned pools
        self.__pools = {poolname: ZPool(pool_data) for poolname, pool_data in json.loads(result.stdout)['pools'].items()}
        return self.__pools

    def display(self, console: rich.console.Console) -> None:
        """
        Display currently gathered statistics from all pools stored in self.__pools

        :param console: The application instance of the Rich Console class to use to output data
        """
        # For each pool, display the stored state to screen
        for poolname, pool in self.__pools.items():
            console.rule(f'ZPool - {poolname}')
            console.print(pool.summary)
            console.print(pool.vdevs)
            console.print()

            console.print(pool.scan_stats)
