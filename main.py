#!/usr/bin/env python
from dotenv import load_dotenv
load_dotenv() 

import tempfile, os
from utils.log import log
from gmail_utils import get_latest_attachment
from sheets_utils import read_sheet, write_sheet
from reconcile import reconcile_frames
import pandas as pd

def main():
    log.info("=== Site‑Problem sync started ===")
    tmp_dir = tempfile.mkdtemp()
    try:
        xlsx_path = get_latest_attachment(tmp_dir)
        if not xlsx_path:
            log.info("No new attachments → exit")
            return

        src_df = pd.read_excel(
            xlsx_path,
            sheet_name=os.getenv("SOURCE_TAB_NAME"),
            header=int(os.getenv("SOURCE_HEADER_ROW")) - 1
        )

        tgt_df = read_sheet()            # returns pandas DF
        updated_df, n_upd, n_warn = reconcile_frames(src_df, tgt_df)

        if n_upd or n_warn:
            write_sheet(updated_df)
            log.success(f"Wrote sheet → {n_upd} updates, {n_warn} warnings.")
        else:
            log.info("No changes needed.")

    finally:
        try:
            os.remove(xlsx_path)
        except Exception:
            pass

if __name__ == "__main__":
    main()
