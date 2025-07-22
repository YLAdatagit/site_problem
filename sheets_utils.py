from googleapiclient.discovery import build
from utils.auth import get_creds
import pandas as pd, os, itertools

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/spreadsheets"
]

def read_sheet() -> pd.DataFrame:
    creds = get_creds(SCOPES)
    sheet = build("sheets", "v4", credentials=creds)
    ss_id  = os.getenv("TARGET_SPREADSHEET_ID")
    tab    = os.getenv("TARGET_TAB_NAME")
    rng = f"'{tab}'"
    result = sheet.spreadsheets().values().get(
        spreadsheetId=ss_id, range=rng, majorDimension="ROWS").execute()
    values = result.get("values", [])
    df = pd.DataFrame(values[1:], columns=values[0])
    return df

def write_sheet(df: pd.DataFrame):
    creds = get_creds(SCOPES)
    service = build("sheets", "v4", credentials=creds)
    ss_id  = os.getenv("TARGET_SPREADSHEET_ID")
    tab    = os.getenv("TARGET_TAB_NAME")
    body = {
        "values": [df.columns.tolist()] + df.fillna("").values.tolist()
    }
    service.spreadsheets().values().update(
        spreadsheetId=ss_id, range=f"'{tab}'",
        valueInputOption="RAW", body=body).execute()
