
# home_dirs_dashboard.py
from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from typing import Dict

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Grid, Vertical

from textual.widgets import Header, Footer, Static, Label
from textual.reactive import reactive
from textual.timer import Timer

from zpoolpanel import ZPoolPanel
from zpool_monitor import Monitor, ZPool, zpool_monitor_argparse



# ====== Configuration ======
REFRESH_SECONDS = 10  # polling interval
# ===========================


class Dashboard(App):
    """
    Textual app that displays a dashboard of tiles for each subdirectory
    in the user's home directory. Tiles are refreshed every REFRESH_SECONDS.
    """
    CSS_PATH = './dashboard.css'

    BINDINGS = [
        ("r", "refresh_now", "Refresh now"),
        ("+", "increase_refresh", "Increase refresh period"),
        ("-", "decrease_refresh", "Decrease refresh period"),
        ("t", "app.toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    # Refresh timer parameters
    refresh_period: reactive[int | None] = reactive(None)

    def __init__(self, arguments, **kwargs):
        super().__init__(**kwargs)
        self.__monitor = Monitor(arguments)
        self.__timer: Timer | None = None

    def compose(self) -> ComposeResult:
        yield Header(icon="🔍", id="header", show_clock=True)
        # Something like this but need to make the panels only as big as they NEED to be
        self._grid = Vertical(id="body")
        yield self._grid
        # This works better, but all panels are equal height and fitted to screen
        # with VerticalScroll(id="body"):
        #     self._grid = Grid(id="panels")
        #     yield self._grid

        yield Footer(id="footer")

    async def on_mount(self) -> None:
        """
        Initial population of the display and install timer for periodic updates
        """
        self.title = "ZPool Monitor"
        await self.refresh_panels()
        self.refresh_period = REFRESH_SECONDS

    # -------------------------------------------
    # Refresh Timer related methods
    def action_increase_refresh(self) -> None:
        """Increase the refresh period by one second up to a maximum of 60 seconds"""
        self.refresh_period = min(self.refresh_period + 1, 60)

    def action_decrease_refresh(self) -> None:
        """Decrease the refresh period by one second down to a maximum of 1 second"""
        self.refresh_period = max(self.refresh_period - 1, 1)

    def watch_refresh_period(self, ) -> None:
        """
        Automatically called when internal refresh_period Reactive variable is changed

        1) Delete current timer (if it exists)
        2) Update application subtitle to display the refresh period on screen
        3) Recreate timer with the new refresh period to call refresh_panels() every refresh_period seconds
        """
        if self.__timer: self.__timer.stop()
        self.sub_title = f'Refresh period: ⏱️ ({self.refresh_period}s)'
        self.__timer = self.set_interval(self.refresh_period)

    # -------------------------------------------
    # Manual refresh related methods
    async def action_refresh_now(self) -> None:
        """
        Activated when user presses "r" to implement an immediate refresh. Call refresh_panels() to update the display
        :return:
        """
        await self.refresh_panels()

    # -------------------------------------------
    # Refreshing dashboard related methods
    async def refresh_panels(self) -> None:
        """
        Use the inbuilt Monitor instance to rescan and update the ZPool status. Then update the ZPoolPanel instances with the new data.

        If a new pool is discovered, it must be added to the set of panels, destroyed pools must be removed.
        """
        # Re-scan all pools on the system
        scanned_pools: Dict[str, ZPool] = await asyncio.to_thread(lambda: self.__monitor.refresh_stats())

        # Retrieve all panels currently monitoring a pool
        current_panels: Dict[str, ZPoolPanel] = {panel.zpool_data.poolname: panel for panel in self._grid.children if isinstance(panel, ZPoolPanel) and panel.zpool_data.poolname}

        # new_pools is a set of all pool names that do not already have a panel
        new_pools = scanned_pools.keys() - current_panels.keys()

        # existing_pools is a set of all pool names that both exist and have an existing panel in the UI
        existing_pools = scanned_pools.keys() & current_panels.keys()

        # removed_pools is a set of all pool names that have panels but are no longer on the system
        removed_pools = current_panels.keys() - scanned_pools.keys()

        # Add new panels
        for poolname in sorted(new_pools):
            panel = ZPoolPanel(scanned_pools[poolname], id=f'panel_{poolname}')
            await self._grid.mount(panel)

        # Update existing panels
        for poolname in existing_pools:
            current_panels[poolname].update_zpool_data((scanned_pools[poolname]))

        # Remove panels for ZPools that no longer exist - to_remove_keys will be all pool names that have panels but are no longer on the system
        for poolname in removed_pools:
            await current_panels[poolname].remove()

        # Optionally, sort tiles by name or size by reordering children
        # Here we keep mounting order; uncomment to sort by name:
        # new_panels: dict[str, ZPoolPanel] = {}
        # for poolname, pool in scanned_pools.items():
        #     if poolname in new_pools:
        #         new_panels[poolname] = ZPoolPanel(pool, id=f'panel_{poolname}')
        #     else:
        #         new_panels[poolname] = current_panels[poolname]
        #         new_panels[poolname].update_zpool_data(pool)
        # await self._grid.remove_children(*self._grid.children)
        # await self._grid.mount(*new_panels.values())


        # ordered = sorted(
        #     [w for w in tiles_grid.children if isinstance(w, DirectoryTile)],
        #     key=lambda w: (w.stats.name.lower() if w.stats else "")
        # )
        # await tiles_grid.remove_children(*tiles_grid.children)
        # await tiles_grid.mount(*ordered)
