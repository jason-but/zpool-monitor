"""
This module implements a series of ArgParse Validators used by applications within the zpool_monitor Python Package.

All Validators are implemented as Classes designed to be used in the context of command-line parsing. Upon failure to validate the command line parameter,
the validators raise a suitable argparse.ArgumentTypeError for the calling argument parsing utilities.

All ArgParse Validator classes implement the __call__(arg) parameter and return the parameter if validation is successful.
"""

# Import System Libraries
import argparse
from textual.theme import BUILTIN_THEMES

# Import zpool_monitor CLI Validators, Monitor Class, and zpool_monitor.textual ZPoolDashboard App
from .systemzpool import get_zpools


class ValidPool:
    """ArgParse Validator to validate if the provided ZPool name exists."""
    # Obtain the list of available pools once to save re-running zpool 'list' command repeatedly
    valid_pools: list[str] = get_zpools()

    def __call__(self, pool) -> str:
        """
        :param pool: Command line argument specifying a ZPool name.
        :return: Parameter pool if validation is successful.
        :raises: Exception argparse.ArgumentTypeError if validation fails.
        """
        if pool in ValidPool.valid_pools: return pool

        raise argparse.ArgumentTypeError(f'{pool} is not a valid pool name. ZPools on system: {', '.join(ValidPool.valid_pools)}')


class ValidTheme:
    """ArgParse Validator to validate if the provided Textual Theme name is valid."""
    # List of themes are extracted from Textual BUILTIN_THEMES
    valid_themes: list[str] = list(BUILTIN_THEMES.keys())

    def __call__(self, theme) -> str:
        """
        :param theme: Command line argument specifying a ZPool name.
        :return: Parameter theme if validation is successful.
        :raises: Exception argparse.ArgumentTypeError if validation fails.
        """
        if theme in ValidTheme.valid_themes: return theme

        raise argparse.ArgumentTypeError(f'{theme} is not a valid theme name, please choose from one of: {', '.join(ValidTheme.valid_themes)}')

    @staticmethod
    def default_theme() -> str:
        """
        :return: First theme listed in Textual Theme pool.
        """
        return ValidTheme.valid_themes[0]
