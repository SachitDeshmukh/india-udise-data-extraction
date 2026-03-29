"""
THIS FILE WILL RETURN DATAFRAME OF INITIAL API RESPONSES FOR SELECT STATE AND DISTRICTS
"""

# IMPORTING NECESSARY LIBRARIES
import pandas as pd
import udise_api_calls.get_all_api_url as api_url  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import udise_api_calls.init_logger as def_log  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import udise_api_calls.obtain_school_data as scl_data  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
from state_report_cards import configuration as report_config

# DEFINING THE GLOBALS
LOGGER = def_log.main(__name__)


# DEFINING THE FUNCTIONS
def create_id_pairs(state_list: list, district_list: list) -> list:
    """
    Create list of dictionaries for state-district pairs from config values.

    Return
    ---
        List of id-pair dicts.
    """
    output_list = []

    for state in state_list:
        for district in district_list:
            state_district_entry = {
                "stateID": state,
                "districtID": district,
            }
            output_list.append(state_district_entry)

    LOGGER.info("All ID pairs were successfully created.")

    return output_list


def get_urls(id_pairs: list) -> list:
    """
    Create custom API call urls by importing function from UDISE-API-CALLS package

    Return
    ---
        list of str entries of api call urls
    """
    url_list = api_url.state_districts_urls(id_pair_list=id_pairs)
    # Log status from imported module

    return url_list


def obtain_school_data(url_list: list) -> pd.DataFrame:
    raw_school_data = scl_data.obtain_school_data(url_list)
    raw_dataframe = scl_data.get_pandas_dataframe(
        raw_school_data
    )  # Prints the dataframe shape

    return raw_dataframe


@def_log.log_documentation_decorator
def main() -> pd.DataFrame:
    """
    Obtain daraframe of raw school level data for select state-district combinations.

    Return
    ---
        Pandas Dataframe
    """
    STATE_IDS = report_config.STATE_ID_LIST
    DISTRICT_IDS = report_config.DISTRICT_ID_LIST

    ID_PAIRS = create_id_pairs(STATE_IDS, DISTRICT_IDS)
    URL_LIST = get_urls(ID_PAIRS)

    RAW_DATA = obtain_school_data(URL_LIST)

    # RAW_DATA.to_csv(
    #     r"C:\Users\Sachit Deshmukh\Documents\Python Scripts\JPAL_UDISE_DATA_EXTRACTION\outputs\temp.csv"
    # )

    return RAW_DATA


if __name__ == "__main__":
    main()
