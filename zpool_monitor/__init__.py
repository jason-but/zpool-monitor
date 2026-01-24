# Try to import the system zpool commands, this will raise an exception if the zpool command does not exist so we need to catch it and exit gracefully
try:
    from .systemzpool import get_zpools, get_zpools_status

except FileNotFoundError as e:
    import rich
    rich.print(f'[bold red]ERROR:[/] {e}')
    exit(1)


# Import all usable types from zpool sub-module
from .zpool import humanise, warning_colour_number, create_progress_renderable, VDEV, VDEVS, ScanStatus, ZPool

from .cliargs import ValidPool, ValidTheme

from .monitor import Monitor

from .apps import zpool_status, zpool_monitor
