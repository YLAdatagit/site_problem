# Column mapping & helper column names
FIELD_MAP = {
    # Map the UID column if it is blank
    "Duplicate in HW DB": {"source": "Unique ID", "mode": "copy_if_blank"},

    # Columns that must always mirror the customer spreadsheet
    "Problem Owner": {
        "source": "Problem Owner",
        "mode": "overwrite",
    },
    "Plan Closed Date": {
        "source": "Plan Closed Date",
        "mode": "overwrite",
    },
    "Problem Clearance Confirm": {
        "source": "Problem Clearance Confirm",
        "mode": "overwrite",
    },
    "Actual Closed Date": {
        "source": "Actual Closed Date",
        "mode": "overwrite",
    },
    "HW Remark": {
        "source": "HW Remark",
        "mode": "overwrite",
    },
}

GS_UID_COL      = "Duplicate in HW DB"
CS_UID_COL      = "Unique ID"
WARNING_COL     = "Warning"
UPDATED_COL     = "Updated Date"
DO_NOT_UPDATE_COL = "DO NOT UPDATE"
