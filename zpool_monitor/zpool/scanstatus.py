"""
This module provides the ScanStatus class which parses the 'zpool status' JSON output for the scan status a single ZPool into internal state. State
information for the ScanStatus can then be accessed as a rich Table for display
"""

# Import System Libraries
from datetime import datetime, timedelta
from typing import Any
from rich import box
from rich.console import RenderableType
from rich.pretty import Pretty
from rich.table import Table

# Import zpool.formatting functions
from . import humanise, create_progress_renderable


class ScanStatus:
    """
    Maps the Scan Status for a single pool to a table for display purposes
    """
    def __init__(self, scan_data: dict[str, Any]):
        """
        Construct instance of class to display the scan status for a single pool

        :param scan_data: JSON Scan Status output for single ZPool from 'zpool status' mapped to a dictionary
        """
        self.__table_title = ''

        # Status information stored in dictionary mapping property to value. Value is stored as a list of Renderables so when a scrub/resilver is progressing
        # the status text and progress bars are neatly organised into columns
        self.__status: dict[str, list[RenderableType]] = {}

        self.__function = scan_data['function']
        # Different method called for each scan type to simplify code reading
        match self.__function:
            case 'SCRUB': self.__get_scrub_status(scan_data=scan_data)
            case 'RESILVER': self.__get_resilver_status(scan_data=scan_data)
            case _: self.__get_unknown_status(scan_data=scan_data)

    def __get_scrub_status(self, scan_data: dict[str, Any]) -> None:
        """
        Parse the Scan Status dictionary for data regarding a scrub, extract information and populate self.__status with data to display in a table when
        retrieved.

        :param scan_data: JSON Scan Status output for single ZPool from 'zpool status' mapped to a dictionary
        """
        self.__table_title = ' 🧼 Scrub Status'

        match scan_data['state']:
            # Table contents for a completed scrub
            case 'FINISHED':
                self.__status['Last Scrub Finished:'] = [f'🕓 {datetime.fromtimestamp(scan_data['end_time']).strftime('%c')}']
                self.__status['Scanned:'] = [f'🔍 {humanise(scan_data['examined'])}']
                self.__status['Duration:'] = [f'⌛ {timedelta(seconds = scan_data['end_time'] - scan_data['start_time'])}']
                self.__status['Repaired:'] = [f'🪛 {humanise(scan_data['processed'])} with {scan_data['errors']} errors']

            # Table contents for an in-progress scrub
            case 'SCANNING':
                to_scan = scan_data['to_examine'] - scan_data['skipped']
                time_elapsed = datetime.now().timestamp() - scan_data['pass_start']
                issued = scan_data['issued']
                scan_complete = 100 * scan_data['examined'] / to_scan
                issue_complete = 100 * issued / to_scan
                issue_rate = max(issued / time_elapsed, 1)
                time_left = timedelta(seconds=round((to_scan - issued) / issue_rate))

                self.__status['Started:'] = [f'🕓 {datetime.fromtimestamp(scan_data['start_time']).strftime('%c')}']
                self.__status['Scanned:'] = [f'🔍 {humanise(scan_data['examined'])} of {humanise(scan_data['to_examine'])}',
                                             create_progress_renderable('', '', scan_complete)]
                self.__status['Issued:'] = [f'🏁 {humanise(issued)} of {humanise(scan_data['to_examine'])} at {humanise(issue_rate)}/s',
                                            create_progress_renderable('', f' ⏳️ {time_left} remaining', issue_complete)]
                self.__status['Repaired:'] = [f'🪛 {humanise(scan_data['processed'])}']

            # Table contents for a scrub with an unknown state
            case _:
                self.__status['Unknown State:'] = [scan_data['state']]
                self.__status['Debug Data:'] = [Pretty(scan_data)]

    def __get_resilver_status(self, scan_data: dict) -> None:
        """
        Parse the Scan Status dictionary for data regarding a scrub, extract information and populate self.__status with data to display in a table when
        retrieved.

        :param scan_data: JSON Scan Status output for single ZPool from 'zpool status' mapped to a dictionary
        """
        self.__table_title = ' 🥈 Resilver Status'

        match scan_data['state']:
            # Table contents for a completed scrub
            case 'FINISHED':
                self.__status['Last Resilver Finished:'] = [f'🕓 {datetime.fromtimestamp(scan_data['end_time']).strftime('%c')}']
                self.__status['Duration:'] = [f'⌛ {timedelta(seconds = scan_data['end_time'] - scan_data['start_time'])}']
                self.__status['Resilvered:'] = [f'🚧 {humanise(scan_data['processed'])} with {scan_data['errors']} errors']

            # Table contents for an in-progress scrub
            case 'SCANNING':
                to_scan = scan_data['to_examine'] - scan_data['skipped']
                time_elapsed = datetime.now().timestamp() - scan_data['pass_start']
                issued = scan_data['issued']
                scan_complete = 100 * scan_data['examined'] / to_scan
                issue_complete = 100 * issued / to_scan
                issue_rate = max(issued / time_elapsed, 1)
                time_left = timedelta(seconds=round((to_scan - issued) / issue_rate))

                self.__status['Started:'] = [f'🕓 {datetime.fromtimestamp(scan_data['start_time']).strftime('%c')}']
                self.__status['Scanned:'] = [f'🔍 {humanise(scan_data['examined'])} of {humanise(scan_data['to_examine'])}',
                                             create_progress_renderable('', '', scan_complete)]
                self.__status['Issued:'] = [f'🏁 {humanise(issued)} of {humanise(scan_data['to_examine'])} at {humanise(issue_rate)}/s',
                                            create_progress_renderable('', f' ⏳️ {time_left} remaining', issue_complete)]
                self.__status['Resilvered:'] = [f'🚧 {humanise(scan_data['processed'])}']

            # Table contents for a scrub with an unknown state
            case _:
                self.__status['Unknown State:'] = [scan_data['state']]
                self.__status['Debug Data:'] = [Pretty(scan_data)]

    def __get_unknown_status(self, scan_data: dict) -> None:
        """
        Application does not understand the current function, print out dictionary for debugging purposes.

        :param scan_data: JSON Scan Status output for single ZPool from 'zpool status' mapped to a dictionary
        """
        self.__table_title = '❌ Unknown Function Status'
        self.__status['Unknown Function:'] = [scan_data['function']]
        self.__status['Unknown State:'] = [scan_data['state']]
        self.__status['Debug Data:'] = [Pretty(scan_data)]

    @property
    def status(self) -> Table:
        """
        :return: Return the Scan Status as a rich Table for display
        """
        table = Table(title=self.__table_title, title_style='bold yellow', title_justify='left', show_header=False, show_lines=False, box=box.SIMPLE)

        for key, value in self.__status.items():
            table.add_row(key, *value)

        return table
