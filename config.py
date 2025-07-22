# Column mapping & helper column names
FIELD_MAP = {
    "Duplicate in HW DB": {"source": "Unique ID", "mode": "copy_if_blank"},
    # … (rest of your mapping)
}

GS_UID_COL      = "Duplicate in HW DB"
CS_UID_COL      = "Unique ID"
WARNING_COL     = "Warning"
UPDATED_COL     = "Updated Date"
DO_NOT_UPDATE_COL = "DO NOT UPDATE"
