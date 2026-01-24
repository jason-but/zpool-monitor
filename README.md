# ZPool Monitor

This package provides a replacement for the standard `zpool status` command to monitor the status of ZPools on your system. Output is colour formatted for 
easier detection of errors and problems to address, progress of running tasks is displayed using a progress bar.

## Installation

To install globally, run:

```console
pip install zpool-monitor
```

At this point the executable programs `zpool_status` and `zpool_monitor` can be executed as a regular command.

### Alternative - Install within a Virtual Environment

To create and install within a Virtual Environment

```console
python -m venv zpool_monitor
. zpool_monitor/bin/activate
pip install zpool-monitor
```

The application binaries are installed in the `zpool_monitor/bin` directory and can be executed as:

```console
zpool_monitor/bin/zpool_status
zpool_monitor/bin/zpool_monitor
```

If you choose, you can soft-link this binary to anywhere else on the system and execture without entering the virtual environment.

## ZPool Status

The first application installed as part of this package is `zpool_status`.

Usage instructions can be seen in the screenshot below.

![zpool_status help](https://github.com/jason-but/zpool-monitor/blob/master/screenshots/zpool_status_help.png)


| Command-line Parameter | Description                                                                                                                                                                                                                                                                                   |
|:-----------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `poolname`             | Same functionality as listing a pool when executing `zpool status [pool]`. If not specified, will default to scanning all pools on system. You can optionally provide as many pool names as you wish. **NOTE: provided names are checked to see if they are valid poolnames on your system.** |

### Execution

Screenshot of execution on a healthy pool.

![zpool_status healthy](https://github.com/jason-but/zpool-monitor/blob/master/screenshots/zpool_status_healthy.png)

The `zpool_status` command offers the following features:

 - Each pool is separated by a horizontal rule
 - Healthy pools/VDEVs are coloured green, any issues will be displayed in a different colour
 - The last scrub/resilver is displayed in a nice table. If a scrub/resilver is in progress, it will be displayed as a progress bar with estimated completion time
 - If a VDEV has been trimmed it will show the last time it was trimmed. If a trim is in progress, it will be displayed as a progress bar

Other screenshots are provided below.

#### Screenshot of Scrub in Progress

TBA...

#### Screenshot of Trim in Progress

TBA...

## ZPool Monitor

The second application installed as part of this package is `zpool_monitor`.

`zpool_monitor` is a [Textual](https://github.com/Textualize/textual) based application that will display a regularly updated dashboard containing the current
ZPool status.

Usage instructions can be seen in the screenshot below.

![zpool_monitor help](https://github.com/jason-but/zpool-monitor/blob/master/screenshots/zpool_monitor_help.png)

| Command-line Parameter | Description                                                                                                                                                                                                                                                                                     |
|:-----------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-r REFRESH`           | Specify the initial refresh period used to update ZPool status. Default is 10 seconds. Period can be updated within the dashboard application.                                                                                                                                                  |
| `-t THEME`             | Specify the initial [Textual](https://github.com/Textualize/textual) theme to use in the dashboard. Theme can be switched within the dashboard application. **NOTE: requested theme is checked to see if it is a valid [Textual](https://github.com/Textualize/textual) theme.**                |
| `poolname`             | Same functionality as listing a pool when executing `zpool status [pool]`. If not specified, will default to monitoring all pools on system. You can optionally provide as many pool names as you wish. **NOTE: provided names are checked to see if they are valid poolnames on your system.** |

### Execution

TBA...

### Navigating the Dashboard

TBA...
