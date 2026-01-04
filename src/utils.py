"""
utils.py

Small helper functions.
Right now, this file only knows how to read the blackout window
from a CSV file.
"""

import csv
from datetime import datetime


def read_blackout_window(csv_path):
    """
    Read a blackout start and end time from a CSV file.

    Expected CSV format:
      blackout_start, blackout_end
      2025-12-20 09:45, 2025-12-20 23:00

    Returns:
      blackout_start (datetime)
      blackout_end   (datetime)
    """

    # Open the CSV file
    with open(csv_path, "r", newline="") as f:
        # Ignore commented lines starting with '#'
        reader = csv.DictReader(row for row in f if not row.startswith("#"))
        row = next(reader)

    # Convert text timestamps into Python datetime objects
    blackout_start = datetime.fromisoformat(row["blackout_start"])
    blackout_end = datetime.fromisoformat(row["blackout_end"])

    return blackout_start, blackout_end
