# reconcile.py
"""
Synchronise the Google‑Sheet dataframe (*tgt*) with the customer dataframe (*src*)
using the same rules as compare_site_problem_excel.py.

Returns (updated_tgt_df, rows_updated, warnings_added)
"""

from __future__ import annotations
from datetime import date
from typing import Tuple, Dict

import pandas as pd

from config import (
    FIELD_MAP,               # dict: {gs_col: {"source": cs_col, "mode": …}}
    GS_UID_COL, CS_UID_COL,  # "Duplicate in HW DB", "Unique ID"
    WARNING_COL, UPDATED_COL, DO_NOT_UPDATE_COL,
)
from utils.log import log

DU_ID_COL = "DU ID"
TODAY = date.today().isoformat()

# ------------------------------------------------------------------ #
# Helper functions
# ------------------------------------------------------------------ #
def norm(v) -> str:
    return str(v).strip().upper()


def build_key(row, cols):
    return "|".join(norm(row[c]) for c in cols)


# ------------------------------------------------------------------ #
# Main reconciliation function
# ------------------------------------------------------------------ #
def reconcile_frames(src: pd.DataFrame,
                     tgt: pd.DataFrame) -> Tuple[pd.DataFrame, int, int]:

    # 1. normalise – treat NAN as blank strings
    src = src.fillna("").astype(str)
    tgt = tgt.fillna("").astype(str)
    src_norm = src.map(norm)
    tgt_norm = tgt.map(norm)

    # 2. drop duplicate UID rows (keep first)
    dupe_uid = src_norm.duplicated(subset=[CS_UID_COL], keep="first")
    if dupe_uid.any():
        log.warning(f"Skipped {dupe_uid.sum()} duplicate UID row(s).")
        src, src_norm = src[~dupe_uid], src_norm[~dupe_uid]

    # 3. composite‑key columns
    key_cols_t = [g for g, m in FIELD_MAP.items() if m["mode"] == "key"]
    key_cols_s = [FIELD_MAP[g]["source"] for g in key_cols_t]

    src["__key"] = src.apply(lambda r: build_key(r, key_cols_s), axis=1)
    tgt["__key"] = tgt.apply(lambda r: build_key(r, key_cols_t), axis=1)
    src_norm["__key"] = src["__key"]

    # 4. drop duplicate composite‑key rows (keep first)
    dupe_key = src_norm.duplicated(subset=["__key"], keep="first")
    if dupe_key.any():
        log.warning(f"Skipped {dupe_key.sum()} duplicate composite‑key row(s).")
        src, src_norm = src[~dupe_key], src_norm[~dupe_key]

    # 5. build look‑up dicts
    src_by_uid: Dict[str, Dict[str, pd.Series]] = {}
    for _, r in src.iterrows():
        uid = norm(r[CS_UID_COL])
        du  = norm(r[DU_ID_COL])
        src_by_uid.setdefault(uid, {})[du] = r

    src_by_key = (
        src.drop_duplicates(subset="__key", keep="first")
           .set_index("__key", drop=False)
           .to_dict("index")
    )

    # 6. ensure helper columns exist
    for col in (WARNING_COL, UPDATED_COL):
        if col not in tgt.columns:
            tgt[col] = ""

    # 7. walk target rows
    updates = warnings = 0

    for idx, row in tgt.iterrows():
        uid = norm(row[GS_UID_COL])
        du  = norm(row[DU_ID_COL])
        srow = None

        # UID + DU‑ID match first
        if uid and uid in src_by_uid:
            srow = src_by_uid[uid].get(du) or next(iter(src_by_uid[uid].values()))

        # fallback to composite key
        if srow is None:
            srow = src_by_key.get(row["__key"])

        # ---------------- apply updates ----------------
        if srow is not None:
            changed = False
            for gs_col, mapping in FIELD_MAP.items():
                cs_col = mapping["source"]
                mode   = mapping["mode"]
                old, new = row[gs_col], srow[cs_col]

                if mode == "overwrite" and old != new:
                    tgt.at[idx, gs_col] = new; changed = True
                elif mode == "copy_if_blank" and old == "":
                    tgt.at[idx, gs_col] = new; changed = True

            if changed:
                tgt.at[idx, UPDATED_COL] = TODAY
                tgt.at[idx, WARNING_COL] = ""
                updates += 1
        else:
            if row.get(DO_NOT_UPDATE_COL, "").strip():
                tgt.at[idx, WARNING_COL] = "⚠ Not Registered"
                warnings += 1

    tgt.drop(columns="__key", inplace=True, errors="ignore")
    return tgt, updates, warnings
