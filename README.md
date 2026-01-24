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
python -m venv zpool_mon
. zpool_mon/bin/activate
pip install zpool-monitor
deactivate
```

The application binaries are installed in the `zpool_mon/bin` directory and can be executed as:

```console
zpool_mon/bin/zpool_status
zpool_mon/bin/zpool_monitor
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

Like all [Textual](https://github.com/Textualize/textual) based apps, the Dashboard can be bound to numerous keys, and can be controlled by the mouse if used on 
a terminal via a GUI.

#### Display

This application is designed as a single-screen Dashboard. This means that all pools will be displayed in panels on the one screen. If the screen is not large
enough to display all pools, each panel will be made smaller with a scrollbar inside of it to enable access of all pool data. As the pool state is always
displayed as the first line of each Panel, you will always be able to see the state of all pools.

If the dashboard is executed to monitor all pools (`[poolname ...]` is not provided), the dashboard is dynamic in that newly added pools will automatically be
added to the dashboard in a new Panel. Similarly, destroyed pools will have their Panels automatically removed.

The contents of the panels are exactly the same data and format as the output of the `zpool_status` command. As such, ongoing **scrubs**, **resilvers**, and
**trims** will be shown as a progress bar. If a **scrub**/**resilver** is ongoing, the ETA is also displayed.

#### Changing the Refresh Period

The initial refresh period can be specified when launching the Dashboard (default=10 seconds). The Dashboard contains three bindings to manage the refresh
period:

| Key Binding | Action                  | Outcome                                                                                                                                                                    |
|:------------|:------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `r`         | Refresh now             | Will cause the Dashboard to perform an immediate refresh of ZPool status and update the display.                                                                            |
| `+`         | Increase refresh period | Will increase the current refresh period by one second. The current period is always displayed in the title bar. **NOTE: Maximum refresh period is capped at 60 seconds.** |
| `-`         | Decrease refresh period | Will decrease the current refresh period by one second. The current period is always displayed in the title bar. **NOTE: Minimum refresh period is capped at 1 seconds.** |

Key bindings for the above actions are always displayed in the Dashboard Footer. You can initiate one of these actions by either pressing the corresponding key,
or by clicking on Footer area with the mouse.

#### Changing the Theme

The initial theme can be specified when launching the Dashboard (default is the default [Textual](https://github.com/Textualize/textual) Theme). The Dashboard
contains two bindings to manage the current theme.

| Key Binding | Action                  | Outcome                                                                                                                                                                                |
|:------------|:------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `d`         | Toggle dark mode (`d`)  | Will toggle the current theme between dark and light mode.                                                                                                                             |
| `t`         | Select new Theme (`t`)  | Will open a selection text box listing all current themes. You may type in your new theme, use the cursor keys and enter to select a new Theme, or use the mouse to select a new Theme |

Key bindings for the above actions are always displayed in the Dashboard Footer. You can initiate one of these actions by either pressing the corresponding key,
or by clicking on Footer area with the mouse.

#### Taking a Screenshot

Other actions available in the Dashboard are via the command palette. This can be accessed by either:

- Typing `Ctrl-p`
- Clicking on the icon in the upper left corner of the Dashboard

This will open a menu where you can choose one of four options.

| Menu Item  | Action                                                                                                                                                                                                                                 |
|:-----------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Keys       | Slides in a Panel to the right displaying help on all available key-bindings. The ZPool panels will shrink horizontally to acommodate the help Panel. To hide the Panel, repeat the process (eg. type `Ctrl-p`, then select **Keys**). |
| Quit       | Quit the Dashboard immediately.                                                                                                                                                                                                        |
| Screenshot | Save the current Dashboard display as an SVG file.                                                                                                                                                                                     |
| Theme      | Open the same selection text box to change Theme as noted in the previous sub-section.                                                                                                                                                 |
