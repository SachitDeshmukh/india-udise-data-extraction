"""
THIS FILE WILL STORE CLEANED REPORT CARD DATA INTO CSV FILE.
"""

# IMPORTING NECESSRY LIBRARIES
import pandas as pd
from urllib.parse import urlparse, parse_qs
from udise_api_calls import *
from state_report_cards import configuration as report_config

import state_report_cards.state_school_data as report_level_1
import state_report_cards.clean_school_id as clean_id
import state_report_cards.report_card_raw as report_level_2


def extract_school_id(url: str) -> str | None:
    """
    Extract the 'schoolId' parameter from a UDISE+ API URL.
    Expansion of `lambda x: int(parse_qs(urlparse(x).query).get("schoolId", [None])[0])`

    Returns
    -------
    str or None
        The extracted schoolId as a string if present,
        otherwise None.
    """

    parsed = urlparse(url)  # Step 1: Parse the URL into components
    query = parsed.query  # Step 2: Extract only the query string part
    params = parse_qs(query)  # Step 3: Convert query string into a dictionary
    school_id_list = params.get("schoolId", [None])  # Step 4: Safely get 'schoolId'
    school_id = int(school_id_list[0])  # Step 5: Extract first value from list as int

    return school_id


def add_school_id_to_data(dataframe: pd.DataFrame, url_col) -> pd.DataFrame:
    dataframe["schoolId"] = dataframe[url_col].apply(extract_school_id)

    return dataframe


def merge_dataframes(
    dataframe_1: pd.DataFrame, dataframe_2: pd.DataFrame, col_name
) -> pd.DataFrame:
    """
    Merge two Dataframes based on common values in a specific column.

    Return
        New Dataframe with merged values.
    """
    merged_dataframe = pd.merge(dataframe_1, dataframe_2, on=col_name, validate="1:1")

    return merged_dataframe


@def_log_dec
def output_clean_csv(dataframe_1, dataframe_2, col_name):
    """
    Main function for `report_card_clean.py`.
    ---

    Merge datasets and save resulting dataframe in a CSV file.
    """
    clean_data = merge_dataframes(dataframe_1, dataframe_2, col_name)
    save_csv(clean_data)

    return clean_data


if __name__ == "__main__":
    LOGGER = def_log_main(__name__)

    LEVEL_1_RAW = report_level_1.main()
    ID_LIST, LEVEL_1_CLEAN = clean_id.main(LEVEL_1_RAW)

    LEVEL_2_RAW = report_level_2.main(ID_LIST)
    URL_COL = report_config.URL_COL
    LEVEL_2_CLEAN = add_school_id_to_data(LEVEL_2_RAW, URL_COL)

    COL_NAME = report_config.MERGE_COL
    output_clean_csv(LEVEL_1_CLEAN, LEVEL_2_CLEAN, COL_NAME)
