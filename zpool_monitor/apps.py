
import rich
import rich.console


import subprocess
import json
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn
from rich.padding import Padding
from rich import box
from datetime import datetime, timedelta
from rich.pretty import Pretty

import argparse

from zpool_monitor.utilities import humanise, dehumanise
from .vdev import VDEV


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


class Monitor:
    def __init__(self, console, arguments):
        self.__console = console
        self.__poolnames = arguments.poolname

        self.__pools = []

    def refresh_stats(self) -> None:
        result = subprocess.run(['zpool', 'status', '-j', '-t'] + self.__poolnames, capture_output=True, text=True, check=True)

        self.__pools = [ZPool(pool_data) for pool_data in json.loads(result.stdout)['pools'].values()]


    def display(self):
        for pool in self.__pools:
            self.__console.rule(f'ZPool - {pool.poolname}')
            self.__console.print(pool.summary)
            self.__console.print(pool.vdevs)
            self.__console.print()

            self.__console.print(pool.scan_stats)
            self.__console.print()


def main(run_extra) -> None:
    parser = argparse.ArgumentParser(description='ZPool Monitor\n\nMonitor status of zpools on system',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     allow_abbrev=False
                                     )
    parser.add_argument('poolname', nargs='*', type=ValidPool(), help='ZPool name to monitor (default is all pools)')

    arguments = parser.parse_args()


    console = rich.console.Console()


    monitor = Monitor(console, arguments)

    monitor.refresh_stats()
    monitor.display()

    from time import sleep

#    sleep(10)

#    monitor.refresh_stats()
#    monitor.display()

    run_extra = False
    if not run_extra: return

    TEST_SCRUB = {
        'function': 'SCRUB',
        'state': 'SCANNING',
        'start_time': 'Fri 16 Jan 2026 23:02:29 AEDT',
        'end_time': '-',
        'to_examine': '76.7G',
        'examined': '76.8G',
        'skipped': '3.12M',
        'processed': '0B',
        'errors': '0',
        'bytes_per_scan': '0B',
        'pass_start': '1768552352',
        'scrub_pause': '-',
        'scrub_spent_paused': '0',
        'issued_bytes_per_scan': '20.1G',
        'issued': '20.1G'
    }


    foo = scrub_stats(TEST_SCRUB)

    console.print(foo.status)
    console.print(vars(foo))


if __name__ == '__main__':
    # For testing/development purposes. Allow running without installing library
    main(False)

