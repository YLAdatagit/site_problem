#!/usr/bin/env python
"""Standalone step to fetch the latest tracker from Gmail.

The script uses :func:`gmail_utils.get_latest_attachment` and prints the
path to the downloaded file.  The Gmail search query comes from the
``GMAIL_QUERY`` environment variable.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from gmail_utils import get_latest_attachment


def main() -> None:
    parser = argparse.ArgumentParser(description="Download newest Excel attachment from Gmail")
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Directory to store the file (defaults to a temp dir)",
    )
    args = parser.parse_args()

    tmp_dir = args.dest or Path(tempfile.mkdtemp())
    path = get_latest_attachment(tmp_dir)
    if path:
        print(path)
    else:
        print("No attachment found")


if __name__ == "__main__":
    main()
