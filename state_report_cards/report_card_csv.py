"""
THIS FILE WILL STORE RAW REPORT CARD DATA FROM API CALLS INTO CSV FILE.
"""

# IMPORTING NECESSARY LIBRARIES
import pandas as pd
import state_report_cards.state_school_data as report_raw
import state_report_cards.clean_school_id as clean_id
import udise_api_calls.init_logger as def_log  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
from udise_api_calls import configuration as api_config

# DEFINING THE GLOBALS
LOGGER = def_log.main(__name__)
BASE_URL = api_config.UDISE_API_BASE_URL


def report_card_urls(id_list: list) -> list:
    """
    Created GET API call URLs for each state-district pair.

    Return
        List of str values for GET API calls.
    """
    all_call_urls = []

    for id in id_list:
        temp_school_data_url = str(
            BASE_URL + f"getSocialData?flag=1&schoolId={id}&yearId=11"
        )
        all_call_urls.append(temp_school_data_url)

    # print(all_call_urls)

    LOGGER.info("All URLs for school level report card data generated.")

    return all_call_urls


@def_log.log_documentation_decorator
def main(id_list):
    REPORT_URLS = report_card_urls(id_list)

    return REPORT_URLS


if __name__ == "__main__":
    data: pd.DataFrame = (
        report_raw.main()
    )  # Ensures that the output from main() is a pandas DataFrame

    id_list = clean_id.main(data)

    main(id_list)
