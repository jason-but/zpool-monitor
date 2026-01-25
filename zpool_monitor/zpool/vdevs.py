"""
This module provides the VDEVS class which parses the 'zpool status' JSON output for all VDEVS in a pool into internal state. State information for the VDEVS
can then be accessed as a rich Table for display
"""

# Import System Libraries
from typing import Any
from rich.table import Table
from rich import box

# Import zpool.VDEV class
from . import VDEV


class VDEVS:
    """
    Maps all VDEVS within a single pool to a table for display purposes
    """
    def __init__(self, vdevs_data:dict[str, Any]):
        """
        Construct instance of class to map status for all VDEVS within a pool

        Calls member method to recursively traverse vdevs_data to populate self.__vdevs

        :param vdevs_data: JSON output for single VDEV from 'zpool status' mapped to a dictionary
        """
        # __vdevs is a list of VDEV instances
        self.__vdevs: list[VDEV] = []

        self.__populate_table(vdevs_data=vdevs_data, depth=0)

    def __populate_table(self, vdevs_data: dict, depth: int) -> None:
        """
        Recursively traverses vdevs_data to create a tree of VDEV devices which are then flattened into a list of VDEV instances in self.__vdevs

        :param depth: Count of depth of VDEV in pool, 0=top level, 1=actual device for no RAID, or RAID type, 2=actual device within RAID
        :param vdevs_data: JSON output (from 'zpool status' mapped to a dictionary) for a single VDEV OR a VDEV containing multiple VDEVs
        """
        for data in vdevs_data.values():
            self.__vdevs.append(VDEV(vdev_data=data, depth=depth))

            if 'vdevs' in data:
                self.__populate_table(vdevs_data=data['vdevs'], depth=depth + 1)

    @property
    def status(self) -> Table:
        """Return a rich Table representing all VDEVS parsed during the constructor"""
        table = Table(*self.__vdevs[0].label_data, title=f' 🔍 Details', title_style='bold yellow', title_justify='left', show_lines=False, box=box.HORIZONTALS)

        for vdev in self.__vdevs:
            table.add_row(*vdev.row_data)

        return table
