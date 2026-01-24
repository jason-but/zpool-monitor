"""
This module provides the zpool_mon() function to run the application. This function will be installed as a script/binary upon package install.
"""

# Import System Libraries
import rich
import rich.console

# Import zpool.formatting functions
from .monitor import Monitor, zpool_monitor_argparse
from .textual import ZPoolDashboard


def zpool_mon() -> None:
    """
    zpool_mon application implementation
    """
    console = rich.console.Console()

    try:
        arguments = zpool_monitor_argparse()

        # Create the Monitor class to allow access to ZPool stats and to refresh them
        monitor = Monitor(arguments=arguments)

        if arguments.refresh:
            # Running in live monitor mode, create and run the ZPoolDashboard textual App
            ZPoolDashboard(monitor=monitor, initial_theme=arguments.theme, initial_refresh=arguments.refresh).run()

        else:
            # Running in CLI mode, get current ZPool data and display to the console
            monitor.refresh_stats()
            monitor.display(console)

    except KeyboardInterrupt:
        pass

    except (Exception,):
        # Use the rich console to display any other exceptions
        console.print_exception()
