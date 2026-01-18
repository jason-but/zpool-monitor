
import rich
import rich.console


from .monitor import Monitor, zpool_monitor_argparse


def zpool_mon() -> None:
    arguments = zpool_monitor_argparse()

    console = rich.console.Console()

    monitor = Monitor(console, arguments)

    monitor.refresh_stats()
    monitor.display()
