"""
THIS IS THE CONFUGURATION FOR STATE REPORT CARD MODULE.
"""

# STATE SCHOOL DATA
STATE_ID_LIST = [
    "127",
]  # MAHARASHTRA
DISTRICT_ID_LIST = [
    "3705",
    "3718",
    "3720",
    "3725",
    "3732",
    "3708",
]  # AKOLA, JALNA, NASHIK, RATNAGIRI, WARDHA

# STORE IDS IN A TEXT FILE

# CLEAN SCHOOL IDS
COLS_TO_KEEP = [
    "schoolId",
    "schoolName",
    "stateName",
    "districtName",
    "schCatDesc",
    "schoolStatusName",
]
FILTER_SCHOOL_VALUES = {
    "schoolStatusName": [
        "DCF not Received",
        "Operational",
        "Sanctioned but not Operational",
    ],
    "schCatDesc": [
        "Pr. Up Pr. and Secondary Only",
        "Pr. with Up.Pr. Sec. and H.Sec.",
        "Primary",
        "Primary with Upper Primary",
    ],
}

# REPORT CARD RAW
API_DATA_SET_LEVEL_2 = "schEnrollmentYearDataTotal"

# REPORT CARD CLEAN
URL_COL = "api_url"  # dataframe column to retrospectively extract school IDs
MERGE_COL = "schoolId"  # dataframe column where the common value is stored
