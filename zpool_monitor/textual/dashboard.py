"""
This module provides the ZPoolDashboard class which subclasses the Textual App class to create a Textual Application that acts as a Dashboard to poll and
display current ZPool status.
"""

# Import System Libraries
import asyncio
from typing import Dict
from itertools import pairwise
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
        ('r', 'refresh_now', 'Refresh now'),
        ('+', 'increase_refresh', 'Increase refresh period'),
        ('-', 'decrease_refresh', 'Decrease refresh period'),
        ('d', 'app.toggle_dark', 'Toggle dark mode'),
        ('t', 'app.change_theme', 'Select new Theme'),
        ('q', 'quit', 'Quit')
    ]

    # Refresh timer parameters
    refresh_period: reactive[int | None] = reactive(None)

    def __init__(self, monitor: Monitor, initial_theme: str, initial_refresh: int, **kwargs):
        """
        Construct the Application class by initialising internal variables.

        :param monitor: Instance of Monitor to be used to fetch updated ZPool data.
        :param initial_refresh: Initial refresh period for App.
        :param kwargs: Arguments to pass to superclass App().
        """
        super().__init__(**kwargs)
        self.__monitor = monitor
        self.theme = initial_theme
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
        yield Header(icon='🔍', id='header')

        self._body = Vertical(classes='panels')
        yield self._body

        yield Footer(id='footer')

    # ---------- Initial Construction ----------
    async def on_mount(self) -> None:
        """
        Initial population of the display and install timer for periodic updates
        """
        self.title = 'ZPool Monitor'
        await self.refresh_panels()
        self.refresh_period = self.__initial_refresh

    # ------------- Private Methods ------------
    # ---------- Height allocation — two-phase ─────────────────────────────────
    #
    # Phase 1 (_calculate_heights):
    #   Reset every panel and scroller to height:auto.  Textual's layout engine
    #   then sizes each panel to its natural content height with no external
    #   influence.  Schedule phase 2 after that layout pass settles.
    #
    # Phase 2 (_apply_heights):
    #   Read panel.outer_size.height.  At height:auto this is the authoritative
    #   natural height — no circular dependency on any prior allocation.
    #   • Fit:      sum(natural_outer) + margin_overhead ≤ available
    #               → do nothing; height:auto already set in phase 1.
    #   • Overflow: apply iterative fair-share on OUTER heights (see below).
    #
    # WHY OUTER HEIGHTS?
    # ------------------
    # Textual uses box-sizing: border-box by default.  Setting
    # panel.styles.height = H (an integer) means the panel's OUTER size
    # (border + padding + content) = H rows.  The content area (for the
    # scroller) = H − gutter_v rows.
    #
    # Therefore the correct pool formula is simply:
    #
    #   pool_outer = available − margin_overhead
    #
    # There is NO subtraction of gutter_v × n.  Border and padding are already
    # included in the outer heights being allocated, and border-box assignment
    # preserves them automatically.
    #
    # The previous version used  pool = available − gutter_v×n − margin_oh,
    # which computed a "content budget" and then assigned those values as if
    # they were outer heights.  Because border-box treats an explicit integer
    # height as the OUTER height, gutter_v×n rows (= 2×n) were silently
    # discarded, producing exactly the n×2 empty rows observed at the bottom.

    def _calculate_heights(self) -> None:
        """
        Sets all ZPool Panel instances to auto-height so that we can properly determine if there are too many rows to fit on the screen, and manually calculate
        the height for each panel
        """
        for panel in self._body.query(ZPoolPanel):
            # For each ZPoolPanel instance in the display, set the height style to auto
            panel.styles.height = "auto"
            try:
                panel.query_one('.zpoolscroller').styles.height = "auto"
            except Exception:
                pass
        self.call_after_refresh(self._apply_heights)

    def _apply_heights(self) -> None:
        """Phase 2 — measure natural heights; leave auto if everything fits,
        otherwise apply iterative fair-share allocation using outer heights."""
        panels: list[ZPoolPanel] = list(self._body.query(ZPoolPanel))

        # Get the number of ZPool Panels
        n = len(panels)
        if not n: return

        # Get total height of the Vertical display
        available: int = self._body.content_size.height
        if available <= 0: return

        # Get the (natural) height of each panel in the display. If any panel reports height 0, then the layout is still finalising, try again
        natural_outer: dict[ZPoolPanel, int] = {}
        for panel in panels:
            h = panel.outer_size.height
            if h == 0:
                self.call_after_refresh(self._apply_heights)
                return
            natural_outer[panel] = h

        # Calculate the reserved rows for margins between each panel
        margin_overhead: int = ((panels[0].styles.margin.top +
                                sum(max(a.styles.margin.bottom, b.styles.margin.top) for a, b in pairwise(panels))) +
                                panels[-1].styles.margin.bottom)

        # Scenario 1: All ZPoolPanels fit within the available space with no need for scrollbars. Simply return and draw the screen as-is (auto height)
        if sum(natural_outer.values()) + margin_overhead <= available: return

        # Scenario 2: ZPoolPanels will not fit, need to calculate fair-share for their heights
        # Remaining rows to allocate
        remaining_rows: int = max(available - margin_overhead, n)
        # List of panels yet to be allocated final heights
        remaining = list(panels)
        # Dictionary mapping panels to allocated height
        allocated: dict[ZPoolPanel, int] = {}

        while remaining:
            # Determine equal share of remaining space
            num_panels = len(remaining)
            fair_share = remaining_rows / num_panels

            # Find all ZPoolPanels that will fit within their allocated fair-share (equal or smaller)
            small_panels = [p for p in remaining if natural_outer[p] <= fair_share]

            if not small_panels:
                # There are NO small panels, equally divide the remaining rows amongst all remaining panels and assign to allocated. Then we are done so break out of loop
                panel_size, extra_rows = divmod(remaining_rows, num_panels)
                for i, p in enumerate(remaining):
                    allocated[p] = panel_size + (1 if i < extra_rows else 0)
                break

            # Remove small panels from the list of panels to process, then loop around and try again
            for p in small_panels:
                # Set height of small_panel to its natural height
                allocated[p] = natural_outer[p]
                # Reduce count of remaining rows available for allocation
                remaining_rows -= natural_outer[p]
                # Remove panel from list of panels to process
                remaining.remove(p)

        # Now that all panel heights have been calculated, set the Panel height and scroller for each panel
        for panel, h in allocated.items():
            panel.styles.height = h
            panel.query_one('.zpoolscroller').styles.height = "1fr"

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

    # ---------- Terminal resize ----------
    def on_resize(self) -> None:
        # After Textual has re-laid out the screen, re-run the allocator.
        self._calculate_heights()

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

        # 1) Remove panels for ZPools that no longer exist (all pool names that have panels but are no longer on the system)
        for poolname in (current_panels.keys() - scanned_pools.keys()):
            await current_panels[poolname].remove()

        # 2) Update display for existing panels (all pool names that both exist and have an existing panel in the UI)
        for poolname in (scanned_pools.keys() & current_panels.keys()):
            current_panels[poolname].update_zpool_data((scanned_pools[poolname]))

        # 3) Add new panels to the system (all pool names that do not already have a panel) ONLY IF there are panels to insert
        if scanned_pools.keys() - current_panels.keys():
            # Construct list of all panels in sorted order (scanned_pools already sorted)
            # - If poolname exists, copy it from current_panels, otherwise provide default of a new ZPoolPanel initialised with the ZPool instance in scanned_pools
            sorted_panels: list[ZPoolPanel] = [current_panels.get(poolname, ZPoolPanel(pool, id=f'panel_{poolname}')) for poolname, pool in scanned_pools.items()]

            # As we are inserting panels and we don't know where they belong, we remove all panels from the display and remount all those in new_panels
            await self._body.remove_children(self._body.children)
            await self._body.mount(*sorted_panels)

        # After the display is refreshed, call _calculate_heights
        self._calculate_heights()


