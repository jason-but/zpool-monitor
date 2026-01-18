"""
This module provides the VDEV class which parses the 'zpool status' JSON output for a single VDEV into internal state. State information for the VDEV
can then be accessed as a list of data to insert into table cells for display
"""

# Import System Libraries
from rich.padding import Padding

# Import zpool_monitor modules
from .utilities import humanise, dehumanise, warning_colour_number, create_progress_renderable

class VDEV:
    """
    Extracts information for a single VDEV as returned by 'zpool status' and provides relevant data as a list for display
    """
    def __init__(self, vdev_data: dict, depth: int):
        """
        Construct instance of class to map status for a single VDEV

        Extracts relevant data from variables within the vdev_dict dictionary

        :param vdev_data: JSON output for single VDEV from 'zpool status' mapped to a dictionary
        :param depth: Count of depth of VDEV in pool, 0=top level, 1=actual device for no RAID, or RAID type, 2=actual device within RAID
        """
        # State information
        self.__state = vdev_data['state']
        match self.__state:
            case 'ONLINE': self.__state_col = '[green]'
            case 'OFFLINE': self.__state_col = '[bold orange3]'
            case 'DEGRADED': self.__state_col = '[bold orange3]'
            case _: self.__state_col = '[bold red]'

        # Device information - Indent VDEV name based on depth for nice output
        self.__name = Padding(f'{self.__state_col}{vdev_data['name']}', (0, 0, 0, depth * 2))
        self.__device = vdev_data.get('devid', vdev_data.get('path', ''))

        # Space is stored as 'phys_space' if this is an actual disk device, otherwise 'def_space' for VDEV containing VDEVS
        self.__size = vdev_data.get('phys_space', vdev_data.get('def_space', ''))

        self.__trim = self.__parse_trim_state(vdev_data) if 'trim_notsup' in vdev_data else ''

        # Error counts
        self.__read_err = vdev_data['read_errors']
        self.__write_err = vdev_data['write_errors']
        self.__chk_err = vdev_data['checksum_errors']

    def __parse_trim_state(self, vdev_data: dict):
        """
        Parse trim state variables for VDEV as output by 'zpool status' and generate a rich renderable to display status

        :param vdev_data: JSON output for single VDEV from 'zpool status' mapped to a dictionary

        :return: Rich renderable to display current trim status
        """
        match vdev_data['trim_notsup']:
            case '0':
                # Trim supported on this VDEV
                match vdev_data['trim_state']:
                    case 'COMPLETE':
                        # Trim not running, return time of last trim as a string
                        return vdev_data['trim_time']
                    case 'ACTIVE':
                        # Trim running, create and return a rich Progress Bar displaying trim progress
                        complete = 100 * dehumanise(vdev_data['trimmed']) / dehumanise(vdev_data['to_trim'])
                        return create_progress_renderable(f'✂️ {vdev_data['trimmed']} of {vdev_data['to_trim']}', '', complete)
                    case '_':
                        # Invalid value for trim state, should not get here
                        raise ValueError(f'Trim state ({vdev_data['trim_state']}) returned by \'zpool status\' is invalid')

            case '1':
                # Trim NOT supported on this VDEV, return empty string
                return ''

            case '_':
                # Invalid value for trim state, should not get here
                raise ValueError(f'Unexpected value (trim_nosup={vdev_data['trim_notsup']}) returned by \'zpool status\'')

    @property
    def row_data(self) -> list:
        """Return a list containing VDEV data to populate a single row of a table for display"""
        return [self.__name, self.__size, f'{self.__state_col}{self.__state}', self.__device, warning_colour_number(self.__read_err),
                warning_colour_number(self.__write_err), warning_colour_number(self.__chk_err), self.__trim]