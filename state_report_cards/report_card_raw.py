"""
THIS FILE WILL STORE RAW REPORT CARD DATA FROM API CALLS INTO CSV FILE.
"""

# IMPORTING NECESSARY LIBRARIES
import pandas as pd
from joblib import Parallel, delayed
from udise_api_calls import *
import state_report_cards.state_school_data as report_level_1  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import state_report_cards.clean_school_id as clean_id  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT

from state_report_cards import configuration as report_config

# DEFINING THE GLOBALS
LOGGER = def_log_main(__name__)
BASE_URL = api_config.UDISE_API_BASE_URL
DATA_SET = report_config.API_DATA_SET_LEVEL_2


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


def obtain_school_data(url_list: list, data_set) -> pd.DataFrame:
    """
    Extracts report card level data for batches of URL in parallel.

    Return
        List of school data dictionaries
    """
    url_batches = list(scl_data_yield(url_list))

    school_data_list = []

    parallel_output = Parallel(
        n_jobs=api_config.PARALLEL_JOBS, backend="multiprocessing"
    )(delayed(scl_data_obtain)(url_batch, data_set) for url_batch in url_batches)
    for output in parallel_output:
        school_data_list.extend(
            output
        )  # ENROLMENT DATA IS IN DICT FORMAT NOT LIST OF DICT

    report_card_raw = scl_data_frame(school_data_list)  # Prints the dataframe shape

    return report_card_raw


@def_log_dec
def output_level_2_raw(id_list):
    """Main function for `report_card_raw.py`.
    ---

    Obtain daraframe of raw enrollment data for select schools.
    """

    REPORT_URLS = report_card_urls(id_list)
    REPORT_RAW_DATA = obtain_school_data(REPORT_URLS, DATA_SET)

    return REPORT_RAW_DATA


if __name__ == "__main__":
    data: pd.DataFrame = (
        report_level_1.output_level_1_raw()
    )  # Ensures that the output from output_level_1_raw() is a pandas DataFrame

    id_list, filtered_data = clean_id.output_school_id_data(data)

    output_level_2_raw(id_list)
