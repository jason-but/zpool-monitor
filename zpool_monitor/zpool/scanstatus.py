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
        # Table title to display when rendering table
        self.__table_title: str = ''

        # Status information stored in dictionary mapping property to value. Value is stored as a list of Renderables so when a scrub/resilver is progressing
        # the status text and progress bars are neatly organised into columns
        self.__status: dict[str, list[RenderableType]] = {}

        self.__function = scan_data['function']
        # Different method called for each scan type to simplify code reading
        match self.__function:
            case 'SCRUB':
                self.__table_title: str = ' 🧼 Scrub Status'

                match scan_data['state']:
                    # Table contents for a completed scrub
                    case 'FINISHED': self.__populate_table_finished(scan_data=scan_data, finished_label='Last Scrub Finished:',
                                                                    show_scanned=True, processed_label='Repaired:', processed_icon='🪛')

                    # Table contents for an in-progress scrub
                    case 'SCANNING': self.__populate_table_scanning(scan_data=scan_data, processed_label='Repaired:', processed_icon='🪛')

                    # Table contents for a scrub with an unknown state
                    case _: self.__populate_table_debug(scan_data=scan_data)

            case 'RESILVER':
                self.__table_title = ' 🥈 Resilver Status'

                match scan_data['state']:
                    # Table contents for a completed resilver
                    case 'FINISHED': self.__populate_table_finished(scan_data=scan_data, finished_label='Last Resilver Finished:',
                                                                    show_scanned=False, processed_label='Resilvered:', processed_icon='🚧')

                    # Table contents for an in-progress resilver
                    case 'SCANNING': self.__populate_table_scanning(scan_data=scan_data, processed_label='Resilvered:', processed_icon='🚧')

                    # Table contents for a resilver with an unknown state
                    case _: self.__populate_table_debug(scan_data=scan_data)

            case _:
                self.__table_title = '❌ Unknown Function Status'

                self.__status['Unknown Function:'] = [scan_data['function']]
                self.__populate_table_debug(scan_data=scan_data)

    def __populate_table_finished(self, scan_data: dict[str, Any], finished_label:str, show_scanned: bool, processed_label: str, processed_icon: str) -> None:
        """
        Parse the Scan Status dictionary for data a completed scan, extract information and populate self.__status with data to display in a table when
        retrieved.

        :param scan_data: JSON Scan Status output for single ZPool from 'zpool status' mapped to a dictionary
        :param finished_label: Label to display as row header for scan_data['end_time']
        :param show_scanned: Should we add a row to show bytes examined
        :param processed_label: Label to display as row header for scan_data['processed']
        :param processed_icon: Icon to display as image for scan_data['processed']
        """
        self.__status[finished_label] = [f'🕓 {datetime.fromtimestamp(scan_data['end_time']).strftime('%c')}']
        if show_scanned: self.__status['Scanned:'] = [f'🔍 {humanise(scan_data['examined'])}']
        self.__status['Duration:'] = [f'⌛ {timedelta(seconds=scan_data['end_time'] - scan_data['start_time'])}']
        self.__status[processed_label] = [f'{processed_icon} {humanise(scan_data['processed'])} with {scan_data['errors']} errors']

    def __populate_table_scanning(self, scan_data: dict[str, Any], processed_label: str, processed_icon: str) -> None:
        """
        Parse the Scan Status dictionary for data an in-progress scan, extract information and populate self.__status with data to display in a table when
        retrieved.

        :param scan_data: JSON Scan Status output for single ZPool from 'zpool status' mapped to a dictionary
        :param processed_label: Label to display as row header for scan_data['processed']
        :param processed_icon: Icon to display as image for scan_data['processed']
        """
        to_scan: int = scan_data['to_examine'] - scan_data['skipped']
        time_elapsed: timedelta = datetime.now().timestamp() - scan_data['pass_start']
        issued: int = scan_data['issued']
        scan_complete: float = 100 * scan_data['examined'] / to_scan
        issue_complete: float = 100 * issued / to_scan
        issue_rate: float = max(issued / time_elapsed.seconds, 1)
        time_left: timedelta = timedelta(seconds=round((to_scan - issued) / issue_rate))

        self.__status['Started:'] = [f'🕓 {datetime.fromtimestamp(scan_data['start_time']).strftime('%c')}']
        self.__status['Scanned:'] = [f'🔍 {humanise(scan_data['examined'])} of {humanise(scan_data['to_examine'])}',
                                     create_progress_renderable(pre_bar_txt='', post_bar_txt='', percentage=scan_complete)]
        self.__status['Issued:'] = [f'🏁 {humanise(issued)} of {humanise(scan_data['to_examine'])} at {humanise(issue_rate)}/s',
                                    create_progress_renderable(pre_bar_txt='', post_bar_txt=f' ⏳️ {time_left} remaining', percentage=issue_complete)]
        self.__status[processed_label] = [f'{processed_icon} {humanise(scan_data['processed'])}']

    def __populate_table_debug(self, scan_data: dict) -> None:
        """
        Application does not understand the current status for display, add some debugging information to table for output.

        :param scan_data: JSON Scan Status output for single ZPool from 'zpool status' mapped to a dictionary
        """
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
