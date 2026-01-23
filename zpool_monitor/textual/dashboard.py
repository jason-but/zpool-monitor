"""
This module provides the ZPoolDashboard class which subclasses the Textual App class to create a Textual Application that acts as a Dashboard to poll and
display current ZPool status.
"""

# Import System Libraries
import asyncio
from typing import Dict
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Grid, Vertical, VerticalGroup
from textual.widgets import Header, Footer
from textual.reactive import reactive
from textual.timer import Timer

# Import zpool_monitor.zpool.ZPool, zpool_monitor.Monitor, and zpool.textual.ZPoolPanel classes
from . import ZPoolPanel
from .. import Monitor
from ..zpool import ZPool


class ZPoolDashboard(App):
    """
    Textual app that manages a Dashboard of ZPoolPanels to monitor the ongoing status of selected ZPools on the system. Features include:

    - Panel contents are refreshed using a timer.
    - Timer period can be manually changed via '+'/'-' key-bindings and mouse on UI.
    - Immediate refresh can be manually triggered via 'r' key-binding and mouse on UI.
    - Theme light/dark mode can be toggled via 'd' key-binding and mouse on UI.
    - Theme can be selected via 't' key-binding and mouse on UI.
    - Help available via ^p key binding and mouse on UI.
    - Panels are scrollable if all data cannot fit within panel
    """
    # ---------- App CSS Style Sheet ----------
    CSS_PATH = './dashboard.css'

    # ---------- Key Bindings ----------
    BINDINGS = [
        ("r", "refresh_now", "Refresh now"),
        ("up", "increase_refresh", "Increase refresh period"),
        ("down", "decrease_refresh", "Decrease refresh period"),
        ("d", "app.toggle_dark", "Toggle dark mode"),
        ("t", "app.change_theme", "Select new Theme"),
        ("q", "quit", "Quit"),
    ]

    # Refresh timer parameters
    refresh_period: reactive[int | None] = reactive(None)

    def __init__(self, monitor: Monitor, initial_refresh: int, **kwargs):
        """
        Construct the Application class by initialising internal variables.

        :param monitor: Instance of Monitor to be used to fetch updated ZPool data.
        :param initial_refresh: Initial refresh period for App.
        :param kwargs: Arguments to pass to superclass App().
        """
        super().__init__(**kwargs)
        self.__monitor = monitor
        self.__initial_refresh = initial_refresh
        self.__timer: Timer | None = None

    # ---------- UI Composition ----------
    def compose(self) -> ComposeResult:
        """
        Construct the dashboard for display by textual.

        Dashboard consists of a Header (with clock), a footer (with key-bindings), and a Vertical layout that will eventually hold one or more instances of
        a ZPoolPanel widget

        :return: A ComposeResult iterable that will yield the sub-widgets for the dashboard.
        """
        yield Header(icon="🔍", id="header")

        self._body = Vertical(classes='panels')
        # self._body = VerticalScroll(classes='panels')
        yield self._body

        yield Footer(id="footer")

    # ---------- Initial Construction ----------
    async def on_mount(self) -> None:
        """
        Initial population of the display and install timer for periodic updates
        """
        self.title = "ZPool Monitor"
        await self.refresh_panels()
        self.refresh_period = self.__initial_refresh

    # ---------- Refresh Timer related methods ----------
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
        self.sub_title = f'Refresh period: (⏱️ {self.refresh_period} seconds)'
        self.__timer = self.set_interval(self.refresh_period, self.refresh_panels)

    # ---------- Manual refresh related methods ----------
    # Manual refresh related methods
    async def action_refresh_now(self) -> None:
        """
        Activated when user presses "r" to implement an immediate refresh. Call refresh_panels() to update the display
        """
        await self.refresh_panels()

    # ---------- Refreshing dashboard related methods ----------
    async def refresh_panels(self) -> None:
        """
        Use the inbuilt Monitor instance to rescan and update the ZPool status. Then update the ZPoolPanel instances with the new data.

        If a new pool is discovered, it must be added to the set of panels, destroyed pools must be removed.
        """
        # Re-scan all pools on the system
        scanned_pools: Dict[str, ZPool] = await asyncio.to_thread(lambda: self.__monitor.refresh_stats())

        # Retrieve all panels currently monitoring a pool
        current_panels: Dict[str, ZPoolPanel] = {panel.zpool_data.poolname: panel for panel in self._body.children if isinstance(panel, ZPoolPanel) and panel.zpool_data.poolname}

        # new_pools is a set of all pool names that do not already have a panel
        new_pools = scanned_pools.keys() - current_panels.keys()

        # existing_pools is a set of all pool names that both exist and have an existing panel in the UI
        existing_pools = scanned_pools.keys() & current_panels.keys()

        # removed_pools is a set of all pool names that have panels but are no longer on the system
        removed_pools = current_panels.keys() - scanned_pools.keys()

        # Add new panels
        for poolname in sorted(new_pools):
            panel = ZPoolPanel(scanned_pools[poolname], id=f'panel_{poolname}')
            await self._body.mount(panel)

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
