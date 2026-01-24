"""
This module provides the ZPoolPanel class which subclasses the Textual Static class to create a Panel that can be displayed in the dashboard. A single
ZPoolPanel widget represents the current status of a single zpool on the system. The Widget contains a reactive member variable to allow a regular refresh
and update of the data being displayed in the Panel.
"""

# Import System Libraries
from rich.table import Table
from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static
from textual.containers import VerticalScroll

# Import zpool_monitor.zpool.ZPool class
from ..zpool import ZPool


class ZPoolPanel(Static):
    """
    Implements a textual renderable Panel to display current statistics for a single ZPool
    """
    # zpool_data is a reactive member variable. watch_zpool_data() will be automatically called when zpool_data is updated
    zpool_data: reactive[ZPool | None] = reactive(None, layout=True)

    def __init__(self, zpool_data: ZPool, *, id: str | None = None) -> None:
        """
        Initialise the Panel by setting the initial ZPool statistics instance and creating variables to track the three Static Widgets
        :param zpool_data: Instance of ZPool containing the current ZPool statistics.
        :param id:
        """
        super().__init__(id=id, classes='zpoolpanel')

        # Update zpool_data without triggering a reactive watch()
        self.set_reactive(ZPoolPanel.zpool_data, zpool_data)

        # Child widgets set in compose()
        self._status_table: Static | None = None
        self._vdevs_table: Static | None = None
        self._scan_table: Static | None = None

    # ---------- Internal Methods ----------
    def _refresh_panel(self) -> None:
        """
        Private method to refresh the static widgets for display
        """
        # If panel is still building, just return as we have no data yet
        if not self.zpool_data: return

        # Update panel title
        self.border_title = f'ZPool: {self.zpool_data.poolname}'

        # Retrieve rich Table display from ZPool instance and update the three Static Widgets
        self._status_table.update(self.zpool_data.summary)
        self._vdevs_table.update(self.zpool_data.vdevs)
        self._scan_table.update(self.zpool_data.scan_stats)

    # ---------- UI Composition ----------
    def compose(self) -> ComposeResult:
        """
        Construct the panel for display by textual.

        Create a scrollable panel (in case we have many ZPools or problems). The panel contains the three tables that will be returned by ZPool for display.

        :return: A ComposeResult iterable that will yield the sub-widgets for the panel.
        """
        with VerticalScroll(classes='zpoolscroller'):
            self._status_table = Static(Table(), id='status_table')
            yield self._status_table

            self._vdevs_table = Static(Table(), id='vdevs_table')
            yield self._vdevs_table

            self._scan_table = Static(Table(), id='scan_table')
            yield self._scan_table

        # Populate the three tables with values from zpool_status
        self._refresh_panel()

    # ---------- Reactive methods: Keep panel synced when updates occur ----------
    def watch_zpool_data(self, _old: ZPool | None, _new: ZPool | None) -> None:
        """
        Triggered when the reactive internal variable zpool_data is changed. We don't care about the changes, we just need to update the Panel

        :param _old: Original copy of ZPool being replaced.
        :param _new: New copy of ZPool stored in zpool_data.
        """
        self._refresh_panel()

    # ---------- Public Methods to allow updating of reactive member variables ----------
    def update_zpool_data(self, new_zpool_data: ZPool) -> None:
        """
        Update ZPool data for this panel with a new instance of ZPool.

        self.zpool_data is a reactive variable, when changed this will trigger the watch and call watch_zpool_data()

        :param new_zpool_data: Class instance of ZPool to replace self.zpool_data
        """
        self.zpool_data = new_zpool_data

