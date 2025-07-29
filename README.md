# Site-Problem Synchronisation

This project syncs data from customer spreadsheets with a target Google Sheet. It reads a daily Excel file from Gmail, applies reconciliation rules, and writes updates back to the Sheet.

## Workflow Overview

1. **main.py** orchestrates the process.
2. **gmail_utils.get_latest_attachment()** downloads the latest Excel attachment matching the Gmail query.
3. **sheets_utils.read_sheet()** loads the target Google Sheet into a pandas DataFrame.
4. **reconcile.reconcile_frames()** compares the customer data with the Google Sheet and applies update rules defined in **config.py**.
5. **sheets_utils.write_sheet()** writes the reconciled DataFrame back to the Sheet.

Temporary files are stored in a temp directory. Logging output is provided by `utils.log`.

## Modules and Key Functions

### main.py
- `main()`: Entry point that ties everything together. It loads environment variables, fetches the latest attachment, reads/writes the sheet, and invokes reconciliation.

### gmail_utils.py
- `get_latest_attachment(tmp_dir)`: Searches Gmail using the `GMAIL_QUERY` environment variable, downloads the newest `.xlsx` or `.xlsm` attachment from the newest matching thread, marks the thread as read, and returns the local file path.

### sheets_utils.py
- `read_sheet()`: Uses the Google Sheets API to read the target spreadsheet defined by `TARGET_SPREADSHEET_ID` and `TARGET_TAB_NAME`. Returns a pandas DataFrame.
- `write_sheet(df)`: Writes the given DataFrame back to the target sheet.

### reconcile.py
- `reconcile_frames(src, tgt)`: Core reconciliation logic. Accepts a DataFrame from the customer spreadsheet (`src`) and the current target sheet (`tgt`). Returns the updated DataFrame along with counts of updated rows and warnings. Helper functions `norm()` and `build_key()` normalise strings and construct composite keys used for matching rows.

### config.py
Defines column mappings and constants used throughout the reconciliation process, such as `FIELD_MAP`, `GS_UID_COL`, `CS_UID_COL`, and names of helper columns like `WARNING_COL` and `UPDATED_COL`.

`FIELD_MAP` specifies how source columns map onto the Google Sheet and whether
values should overwrite existing cells or only fill blanks. Critical operational
fields such as `Problem Owner`, `Plan Closed Date`, `Problem Clearance Confirm`,
`Actual Closed Date` and `HW Remark` are mapped with `mode: "overwrite"` so the
customer values always replace what is currently on the sheet. Any field marked
`mode: "copy_if_blank"` is also used to build a fallback composite key when no
exact UID/DU‑ID match is found.

### utils/auth.py
- `get_creds(scopes)`: Handles OAuth2 authorisation, storing credentials in `token.json` and refreshing them when necessary. The cached
  token remembers previously granted scopes so the browser consent screen is
  only shown the first time or when new scopes are added.

### utils/log.py
Provides a simple logging utility with functions `info()`, `success()`, `warning()`, and `error()`. The `log` instance from this module is imported wherever logging is needed.

## Running the Script

1. Install dependencies from `requirements.txt`.
2. Set the following environment variables:
   - `GMAIL_QUERY` – Gmail search string used to find the daily Excel file.
   - `SOURCE_TAB_NAME` – Name of the worksheet inside the downloaded file.
   - `SOURCE_HEADER_ROW` – Row number of the header row in that worksheet.
   - `TARGET_SPREADSHEET_ID` – ID of the Google Sheet to update.
   - `TARGET_TAB_NAME` – Name of the tab within the target spreadsheet.
3. Place `credentials.json` from your Google Cloud project in the repository root.
4. Run `python main.py`.

The script will fetch the latest spreadsheet from Gmail, reconcile it with the Google Sheet, and update the sheet accordingly.

## Standalone Scripts

Two utility scripts are included for manual steps:

1. `gmail_download.py` downloads the latest Excel attachment from Gmail and prints the file path.
2. `compare_site_problem_excel.py` compares two Excel workbooks locally using the same rules as `reconcile.py`. The updated Google-sheet export is written alongside the original file.

These scripts are helpful for testing the logic before running `main.py`.
