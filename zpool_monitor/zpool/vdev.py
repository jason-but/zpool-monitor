"""
This module provides the VDEV class which parses the 'zpool status' JSON output for a single VDEV into internal state. State information for the VDEV
can then be accessed as a list of data to insert into table cells for display
"""

# Import System Libraries
from datetime import datetime
from typing import Any
from rich.console import RenderableType
from rich.padding import Padding

# Import zpool.formatting functions
from . import humanise, warning_colour_number, create_progress_renderable


class VDEV:
    """
    Extracts information for a single VDEV as returned by 'zpool status' and converts into Rich Renderables for display as a table with other VDEV instances
    """
    state_colours: dict[str, str] = {'ONLINE': '[green]', 'OFFLINE': '[bold orange3]', 'DEGRADED': '[bold orange3]'}

    def __init__(self, vdev_data: dict[str, Any], depth: int):
        """
        Construct instance of class to map status for a single VDEV

        Extracts relevant data from variables within the vdev_dict dictionary

        :param vdev_data: JSON output for single VDEV from 'zpool status' mapped to a dictionary
        :param depth: Count of depth of VDEV in pool, 0=top level, 1=actual device for no RAID, or RAID type, 2=actual device within RAID
        """
        # Extract VDEV size - done here as this is a number not a string
        vdev_size = vdev_data.get('phys_space', vdev_data.get('def_space', 0))

        # Extract information into dictionary mapping column headers to data as a Rich Renderable, column order is the key order listed here, special cases:
        #   - VDEV name indented to represent depth. Name and state is coloured based on VDEV state
        #   - Trim renderable calculated by __parse_trim_state() method due to multiple possibilities
        self.__data: dict[str, RenderableType] = {'Device Name': Padding(f'{VDEV.state_colours.get(vdev_data['state'], '[bold red]')}{vdev_data['name']}', (0, 0, 0, depth * 2)),
                                                  'Size': humanise(vdev_size) if vdev_size > 0 else '',
                                                  'State': f'{VDEV.state_colours.get(vdev_data['state'], '[bold red]')}{vdev_data['state']}',
                                                  'Device': vdev_data.get('devid', vdev_data.get('path', '')),
                                                  'Read': warning_colour_number(vdev_data['read_errors']),
                                                  'Write': warning_colour_number(vdev_data['write_errors']),
                                                  'Checksum': warning_colour_number(vdev_data['checksum_errors']),
                                                  'Last Trim': self.__parse_trim_state(vdev_data)
                                                  }

    def __parse_trim_state(self, vdev_data: dict[str, Any]) -> RenderableType:
        """
        Parse trim state variables for VDEV as output by 'zpool status' and generate a rich renderable to display trim status

        :param vdev_data: JSON output for single VDEV from 'zpool status' mapped to a dictionary

        :return: Rich renderable to display current trim status
        """
        # VDEV is not a real device, return en empty string
        if 'trim_notsup' not in vdev_data: return ''

        match vdev_data['trim_notsup']:
            case 0:
                # Trim supported on this VDEV
                match vdev_data['trim_state']:
                    case 'UNTRIMMED':
                        # Never trimmed, return string indicating this
                        return f'❌ Never been trimmed'
                    case 'COMPLETE':
                        # Trim not running, return time of last trim as a string
                        return datetime.fromtimestamp(vdev_data['trim_time']).strftime('%c')
                    case 'ACTIVE':
                        # Trim running, create and return a rich Progress Bar displaying trim progress
                        complete = 100 * vdev_data['trimmed'] / vdev_data['to_trim']
                        return create_progress_renderable(pre_bar_txt=f'✂️ {humanise(vdev_data['trimmed'])} of {humanise(vdev_data['to_trim'])}',
                                                          post_bar_txt='',
                                                          percentage=complete)
                    case '_':
                        # Invalid value for trim state, should not get here
                        raise ValueError(f'Trim state ({vdev_data['trim_state']}) returned by \'zpool status\' is invalid')

            case 1:
                # Trim NOT supported on this VDEV, return empty string
                return ''

            case _:
                # Invalid value for trim state, should not get here
                raise ValueError(f'Unexpected value (trim_nosup={vdev_data['trim_notsup']}) returned by \'zpool status\'')

        raise ValueError(f'Unexpected error parsing trim state')

    @property
    def label_data(self) -> list[str]:
        """Return a list containing VDEV column labels to set up the header of a table for display"""
        return list(self.__data.keys())

    @property
    def row_data(self) -> list[RenderableType]:
        """Return a list (as a table row) containing Rich renderables for each column label for display"""
        return list(self.__data.values())
