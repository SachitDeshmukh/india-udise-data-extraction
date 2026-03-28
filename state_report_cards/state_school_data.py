"""
THIS FILE WILL RETURN DATAFRAME OF INITIAL API RESPONSES FOR SELECT STATE AND DISTRICTS
"""

# IMPORTING NECESSARY LIBRARIES
import udise_api_calls.get_all_api_url as api_url  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import udise_api_calls.init_logger as def_log  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
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


def main():
    STATE_IDS = report_config.STATE_ID_LIST
    DISTRICT_IDS = report_config.DISTRICT_ID_LIST

    ID_PAIRS = create_id_pairs(STATE_IDS, DISTRICT_IDS)
    URL_LIST = get_urls(ID_PAIRS)

    # print(URL_LIST)
    return URL_LIST


if __name__ == "__main__":
    LOGGER.info(f"Running the code: {__file__}")  # FOR DOCUMENTATION
    LOGGER.debug(f"Running the code: {__file__}")  # FOR DOCUMENTATION

    main()

    LOGGER.info("Run complete.")
    LOGGER.debug("Run complete.")
