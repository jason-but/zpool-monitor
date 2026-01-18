"""
This module provides some simple utility functions that can be used elsewhere in the application
"""

# Import System Libraries
import re
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


def dehumanise(size: str) -> float:
    """
    Convert human-readable size string to a floating point number (e.g. '2K' --> 2048.0)

    :param size: String to convert

    :return: Number converted to floating point in base Units
    """
    # Split string into number followed by size prefix
    pattern = r"^(\d+\.?\d*)([a-zA-Z]+)$"
    match = re.match(pattern, size)
    if not match: raise ValueError(f"Can't convert {size!r} to bytes")

    units = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4, 'P': 1024**5}
    if match.group(2) not in units: raise ValueError(f"Suffix {match.group(2)} is invalid")

    return float(match.group(1)) * units[match.group(2)]


def warning_colour_number(num_str: str) -> str:
    """Return the provided string coloured as a warning if the string is not the value '0'"""
    return f'{'[bold orange3]' if num_str != '0' else ''}{num_str}'


def create_progress_renderable(pre_bar_txt: str, post_bar_txt: str, percentage: float) -> Progress:
    progress = Progress(TextColumn(pre_bar_txt), BarColumn(), '[process.percentage]{task.percentage:>6.2f}%' + post_bar_txt)
    task = progress.add_task(total=100, description='')
    progress.update(task, completed=percentage)
    return progress