#!/usr/bin/env python
"""Compare two Excel workbooks locally using ``reconcile_frames``.

This mirrors the logic used when updating the Google Sheet but writes
an updated copy of the Google export to disk.  It is useful for
debugging the reconciliation rules before running ``main.py``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from reconcile import reconcile_frames


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Google export with customer tracker")
    parser.add_argument("--google", required=True, type=Path, help="Path to Google-sheet Excel export")
    parser.add_argument("--customer", required=True, type=Path, help="Path to customer tracker Excel file")
    args = parser.parse_args()

    gs_df = pd.read_excel(args.google, sheet_name="Site Problem", dtype=str).fillna("")
    cs_df = pd.read_excel(args.customer, sheet_name="Site Problem (BMA)", header=2, dtype=str).fillna("")

    updated_df, n_upd, n_warn = reconcile_frames(cs_df, gs_df)

    out_path = args.google.with_stem(args.google.stem + "_updated")
    updated_df.to_excel(out_path, index=False)

    print(f"\N{check mark} Updated rows: {n_upd}")
    print(f"\N{warning sign} Missing escalated rows: {n_warn}")
    print(f"Saved updated Google sheet to: {out_path}")


if __name__ == "__main__":
    main()
