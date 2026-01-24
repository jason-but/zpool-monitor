"""
This module provides the Monitor class which can track multiple ZPools and output their status for display.
"""

# Import System Libraries
import rich.console

# Import zpool.ZPool class
from .zpool import ZPool
from .systemzpool import get_zpools_status


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
        # Retrieve current status for all ZPools listed in self.__poolnames and convert to instances of ZPool
        self.__pools = {poolname: ZPool(pool_data) for poolname, pool_data in get_zpools_status(self.__poolnames).items()}

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
