
import rich
import rich.console


from .monitor import Monitor, zpool_monitor_argparse


def zpool_mon() -> None:
    arguments = zpool_monitor_argparse()
    monitor = Monitor(arguments)

    console = rich.console.Console()

    monitor.refresh_stats()
    monitor.display(console)
