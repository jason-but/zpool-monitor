"""
This module provides the VDEV class which parses the 'zpool status' JSON output for a single VDEV into internal state. State information for the VDEV
can then be accessed as a list of data to insert into table cells for display
"""

# Import System Libraries
from datetime import datetime
from rich.padding import Padding

# Import zpool.formatting functions
from . import humanise, warning_colour_number, create_progress_renderable


class VDEV:
    """
    Extracts information for a single VDEV as returned by 'zpool status' and provides relevant data as a list for display
    """
    state_colours: dict[str, str] = {'ONLINE': '[green]', 'OFFLINE': '[bold orange3]', 'DEGRADED': '[bold orange3]'}

    def __init__(self, vdev_data: dict, depth: int):
        """
        Construct instance of class to map status for a single VDEV

        Extracts relevant data from variables within the vdev_dict dictionary

        :param vdev_data: JSON output for single VDEV from 'zpool status' mapped to a dictionary
        :param depth: Count of depth of VDEV in pool, 0=top level, 1=actual device for no RAID, or RAID type, 2=actual device within RAID
        """
        # Extract VDEV size - done here as this is a number not a string
        vdev_size = vdev_data.get('phys_space', vdev_data.get('def_space', 0))

        # Table row consists of:
        # 1) VDEV name indented to represent depth. Name is coloured based on VDEV state
        # 2) If the VDEV has a size, the humanised display of size, otherwise an empty string
        # 3) VDEV state coloured based on current state
        # 4) VDEV device ID, if this doesn't exist, then the VDEV path. If neither exist, empty string
        # 5, 6, 7) Read/Write/Checksum error, coloured as a warning
        # 8) If the VDEV is trimmable, the current trim state (as returned by __parse_trim_state(), otherwise an empty string
        self.__row_data = [Padding(f'{VDEV.state_colours.get(vdev_data['state'], '[bold red]')}{vdev_data['name']}', (0, 0, 0, depth * 2)),
                           humanise(vdev_size) if vdev_size > 0 else '',
                           f'{VDEV.state_colours.get(vdev_data['state'], '[bold red]')}{vdev_data['state']}',
                           vdev_data.get('devid', vdev_data.get('path', '')),
                           warning_colour_number(vdev_data['read_errors']),
                           warning_colour_number(vdev_data['write_errors']),
                           warning_colour_number(vdev_data['checksum_errors']),
                           self.__parse_trim_state(vdev_data) if 'trim_notsup' in vdev_data else ''
                           ]

    def __parse_trim_state(self, vdev_data: dict):
        """
        Parse trim state variables for VDEV as output by 'zpool status' and generate a rich renderable to display status

        :param vdev_data: JSON output for single VDEV from 'zpool status' mapped to a dictionary

        :return: Rich renderable to display current trim status
        """
        match vdev_data['trim_notsup']:
            case 0:
                # Trim supported on this VDEV
                match vdev_data['trim_state']:
                    case 'COMPLETE':
                        # Trim not running, return time of last trim as a string
                        return datetime.fromtimestamp(vdev_data['trim_time']).strftime('%c')
                    case 'ACTIVE':
                        # Trim running, create and return a rich Progress Bar displaying trim progress
                        complete = 100 * vdev_data['trimmed'] / vdev_data['to_trim']
                        return create_progress_renderable(f'✂️ {humanise(vdev_data['trimmed'])} of {humanise(vdev_data['to_trim'])}', '', complete)
                    case '_':
                        # Invalid value for trim state, should not get here
                        raise ValueError(f'Trim state ({vdev_data['trim_state']}) returned by \'zpool status\' is invalid')

            case 1:
                # Trim NOT supported on this VDEV, return empty string
                return ''

            case _:
                # Invalid value for trim state, should not get here
                raise ValueError(f'Unexpected value (trim_nosup={vdev_data['trim_notsup']}) returned by \'zpool status\'')

    @property
    def row_data(self) -> list:
        """Return a list containing VDEV data to populate a single row of a table for display"""
        return self.__row_data
