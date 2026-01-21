"""
This module provides the Monitor class which can track multiple ZPools and output their status for display.
"""
# Import System Libraries
import argparse
import subprocess
import json
import rich.console

# Import zpool_monitor modules
from .zpool import ZPool


# ---------- ArgParse Validators ----------
class ValidPool:
    """
    Provides a callable object to validate if a given pool name is a valid ZPool.

    This class is designed to be used for validating ZPool names in the context of command-line argument parsing. When an instance of this class is called
    with a zpool name, it checks if the pool exists on the system. If the pool does not exist, it raises an error suitable for argument parsing utilities.
    """
    def __call__(self, arg) -> str:
        result = subprocess.run(['zpool', 'list', '-H', '-o', 'name'], capture_output=True, text=True, check=True)
        valid_pools = result.stdout.splitlines()
        if arg in valid_pools: return arg

        raise argparse.ArgumentTypeError(f'{arg} is not a valid pool name.')


# ---------- ArgParse Function ----------
def zpool_monitor_argparse() -> argparse.Namespace:
    """
    Create and return the argument parser for the zpool_monitor

    :return: Namespace containing all command line arguments after parsing
    """
    parser = argparse.ArgumentParser(description='🔍 ZPool Status Monitor\n\nA \'pretty\' replacement for the \'zpool status\' command',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     allow_abbrev=False
                                     )
    parser.add_argument('poolname', nargs='*', type=ValidPool(), help='ZPool name to monitor (default is all pools)')

    return parser.parse_args()


# ---------- Monitor Class ----------
class Monitor:
    def __init__(self, arguments: argparse.Namespace):
        """
        Construct instance of class to monitor multipl ZPool instances

        :param arguments: Command line parameters as parsed by zpool_monitor_argparse()
        """
        self.__arguments = arguments

        # List containing statistics for all pools scanned
        self.__pools: dict[str, ZPool] = {}

    def refresh_stats(self) -> dict[str, ZPool]:
        """
        Refresh the data stored in self.__pools by running 'zpool status' and parsing the output
        """
        # Import output of 'zpool status -t -j' for all nominated pools into a string
        result = subprocess.run(['zpool', 'status', '-t', '-j', '--json-int'] + self.__arguments.poolname, capture_output=True, text=True, check=True)

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
