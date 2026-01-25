"""
This module provides the ZPool class which parses the 'zpool status' JSON output for the status of a single ZPool into internal state. State information for
the pool can then be accessed as rich renderables for display
"""

# Import System Libraries
from typing import Any
from rich import box
from rich.console import RenderableType
from rich.table import Table

# Import zpool.VDEV and zpool.ScanStatus classes
from . import VDEVS, ScanStatus


class ZPool:
    def __init__(self, pool_data: dict[str, Any]):
        """
        Construct instance of class to display the status for a single pool

        :param pool_data: JSON Status output for single ZPool from 'zpool status' mapped to a dictionary
        """
        self.__name: str = pool_data['name']
        state_col = {'ONLINE': '[bold green]', 'OFFLINE': '[bold orange3]⚠️ ', 'DEGRADED': '[bold orange3]⚠️ '}

        self.__data: dict[str, RenderableType] = {'State:': f'{state_col.get(pool_data['state'], '[bold red]⚠️ ')}{pool_data['state']}'}
        if 'status' in pool_data: self.__data['Status:'] = f'[red]🚩 {pool_data['status'].translate(str.maketrans('\n', ' ', '\t'))}'
        if 'action' in pool_data: self.__data['Action:'] = f'[red]📝 {pool_data['action'].translate(str.maketrans('\n', ' ', '\t'))}'
        self.__data['Errors:'] = 'No known data errors' if pool_data['error_count'] == 0 else f'[red]⚠️ Detected {pool_data['error_count']} data errors'

        self.__vdevs = VDEVS(vdevs_data=pool_data['vdevs'])

        # If the pool contains scan information, store them in __scan_stats
        self.__scan_stats = ScanStatus(scan_data=pool_data['scan_stats']) if 'scan_stats' in pool_data else None

    @property
    def poolname(self) -> str:
        """
        :return: Return the name of the pool as a string
        """
        return self.__name

    @property
    def summary(self) -> Table:
        """
        :return: Return summary information about the pool as a rich Table for display
        """
        table = Table('Property', 'Value', show_header=False, show_lines=False, box=box.SIMPLE)
        for key, value in self.__data.items():
            table.add_row(key, value)

        return table

    @property
    def vdevs(self) -> Table:
        """
        :return: Return information about the VDEVs in the pool as a rich renderable for display
        """
        return self.__vdevs.status

    @property
    def scan_stats(self) -> Table:
        """
        :return: Return the Scan Status as a rich renderable for display, if no scan stats are available, return an empty Table
        """
        return self.__scan_stats.status if self.__scan_stats else Table()
