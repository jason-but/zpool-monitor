"""
This module provides the ZPool class which parses the 'zpool status' JSON output for the status of a single ZPool into internal state. State information for
the pool can then be accessed as rich renderables for display
"""

# Import System Libraries
from rich import box
from rich.table import Table

# Import zpool_monitor modules
from .utilities import humanise, dehumanise, warning_colour_number, create_progress_renderable
from .vdevs import VDEVS
from .scanstatus import ScanStatus


class ZPool:
    def __init__(self, pool_data: dict):
        """
        Construct instance of class to display the status for a single pool

        :param pool_data: JSON Status output for single ZPool from 'zpool status' mapped to a dictionary
        """
        self.__name = pool_data['name']
        state_col = {'ONLINE': '[bold green]', 'OFFLINE': '[bold orange3]⚠️ ', 'DEGRADED': '[bold orange3]⚠️ '}

        self.__data = {'State:': f'{state_col.get(pool_data['state'], '[bold red]⚠️ ')}{pool_data['state']}'}
        if 'status' in pool_data: self.__data['Status:'] = f'[red]🚩 {pool_data['status'].translate(str.maketrans('\n', ' ', '\t'))}'
        if 'action' in pool_data: self.__data['Action:'] = f'[red]📝 {pool_data['action'].translate(str.maketrans('\n', ' ', '\t'))}'
        self.__data['Errors:'] = 'No known data errors' if pool_data['error_count'] == '0' else f'[red]⚠️ Detected {pool_data} data errors'

        self.__vdevs = VDEVS(pool_data['vdevs'])

        # If the pool contains scan information, store them in __scan_stats
        self.__scan_stats = ScanStatus(pool_data['scan_stats']) if 'scan_stats' in pool_data else None

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
        summary_table = Table('Property', 'Value', show_header=False, show_lines=False, box=box.SIMPLE)
        for key, value in self.__data.items():
            summary_table.add_row(key, value)

        return summary_table

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
