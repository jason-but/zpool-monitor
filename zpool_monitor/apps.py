"""
This module provides the zpool_mon() function to run the application. This function will be installed as a script/binary upon package install.
"""

# Import System Libraries
import argparse
import rich
import rich.console

# Import zpool_monitor CLI Validators, Monitor Class, and zpool_monitor.textual ZPoolDashboard App
from . import ValidPool, ValidTheme, Monitor
from .textual import ZPoolDashboard


# ---------- APPLICATION: zpool_status ----------
def zpool_status_argparse() -> argparse.Namespace:
    """
    Parses and returns the command-line arguments for the zpool_status application.

        usage: zpool_status [-h] [poolname ...]

    :returns: argparse.Namespace: A Namespace object containing the parsed command-line arguments.

    :raises: This function will raise errors related to incorrect command-line argument parsing using argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(description='🔍 ZPool Status Monitor\n\nA \'pretty\' replacement for the \'zpool status\' command',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     allow_abbrev=False
                                     )

    parser.add_argument('poolname', nargs='*', type=ValidPool(), help='ZPool name to monitor (default is all pools)')

    return parser.parse_args()


def zpool_status() -> None:
    """
    Function executed when installed application zpool_status is executed

    Reads current ZPool status information, displays to screen, and exits.
    """
    console = rich.console.Console()

    try:
        arguments = zpool_status_argparse()

        # ZPool status is retrieved from the Monitor class. We need to refresh the status before displaying them
        monitor = Monitor(poolnames=arguments.poolname)
        monitor.refresh_stats()
        monitor.display(console)

    except KeyboardInterrupt:
        pass

    except (Exception,):
        # Use the rich console to display any other exceptions
        console.print_exception()


# ---------- APPLICATION: zpool_monitor ----------
DEFAULT_REFRESH = 10  # default polling interval


def zpool_monitor_argparse() -> argparse.Namespace:
    """
    Parses and returns the command-line arguments for the zpool_status application.

        usage: zpool_monitor [-h] [-r REFRESH] [-t THEME] [poolname ...]

    :returns: argparse.Namespace: A Namespace object containing the parsed command-line arguments.

    :raises: This function will raise errors related to incorrect command-line argument parsing using argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(description='🔍 ZPool Status Monitor\n\nA \'pretty\' replacement for the \'zpool status\' command',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     allow_abbrev=False
                                     )

    parser.add_argument('-r', '--refresh', type=int, default=DEFAULT_REFRESH, help=f'Monitor update refresh period (default = {DEFAULT_REFRESH})')

    parser.add_argument('-t', '--theme', type=ValidTheme(), default=ValidTheme.default_theme(),
                        help=f'Select application theme (default={ValidTheme.default_theme()})\nValid Themes:\n o {'\n o '.join(ValidTheme.valid_themes)}\n')

    parser.add_argument('poolname', nargs='*', type=ValidPool(), help='ZPool name to monitor (default is all pools)')

    return parser.parse_args()


def zpool_monitor() -> None:
    """
    Function executed when installed application zpool_monitor is executed

    Runs the ZPoolDashboard Textual application to poll ZPool status for display.
    """
    console = rich.console.Console()

    try:
        arguments = zpool_monitor_argparse()

        # ZPool status is retrieved from the Monitor class which is passed to the Textual ZPoolDashboard app for management.
        ZPoolDashboard(monitor=Monitor(poolnames=arguments.poolname), initial_theme=arguments.theme, initial_refresh=arguments.refresh).run()

    except KeyboardInterrupt:
        pass

    except (Exception,):
        # Use the rich console to display any other exceptions
        console.print_exception()
