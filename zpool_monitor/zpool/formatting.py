"""
This module provides some simple utility functions that can be used elsewhere in the application
"""

# Import System Libraries
import math
from rich.progress import Progress, BarColumn, TextColumn


def humanise(size: float) -> str:
    """
    Convert floating point number to human-readable size string (e.g., 2048 --> '2K')

    :param size: Floating point number

    :return: String representation of number converted to Kibibyte format with prefix only
    """
    if size == 0: return '0B'

    units = ['B', 'K', 'M', 'G', 'T', 'P']
    index = int(math.floor(math.log(size, 1024)))
    index = min(index, len(units) - 1)

    return f'{size / (1024 ** index):.2f}{units[index]}'


def warning_colour_number(num: int) -> str:
    """Return the provided number as a string, string is coloured if the number is not 0"""
    return f'{'[bold orange3]' if num != 0 else ''}{num}'


def create_progress_renderable(pre_bar_txt: str, post_bar_txt: str, percentage: float) -> Progress:
    """
    Create and return a rich Progress renderable with the progress bar advanced to the nominated percentage.

    :param pre_bar_txt: Text to insert before the physical progress bar
    :param post_bar_txt: Text to insert after the progress bar AND a percentage complete display
    :param percentage: Advance progress of Progress to 'percentage' complete

    :return: Rich Progress Renderable decorated/set with the provided properties
    """
    progress = Progress(TextColumn(pre_bar_txt), BarColumn(complete_style='cyan1'), '[process.percentage]{task.percentage:>6.2f}%' + post_bar_txt)
    task = progress.add_task(total=100, description='')
    progress.update(task, completed=percentage)
    return progress
