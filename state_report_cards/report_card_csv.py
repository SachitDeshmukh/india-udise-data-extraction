"""
THIS FILE WILL STORE RAW REPORT CARD DATA FROM API CALLS INTO CSV FILE.
"""

# IMPORTING NECESSARY LIBRARIES
import pandas as pd
from joblib import Parallel, delayed
import state_report_cards.state_school_data as report_raw  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import state_report_cards.clean_school_id as clean_id  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import udise_api_calls.init_logger as def_log  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import udise_api_calls.obtain_school_data as scl_data  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
from udise_api_calls import configuration as api_config
from state_report_cards import configuration as report_config

# DEFINING THE GLOBALS
LOGGER = def_log.main(__name__)
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
    url_batches = list(scl_data.yield_url_batches(url_list))

    school_data_list = []

    parallel_output = Parallel(
        n_jobs=api_config.PARALLEL_JOBS, backend="multiprocessing"
    )(
        delayed(scl_data.obtain_school_data)(url_batch, data_set)
        for url_batch in url_batches
    )
    for output in parallel_output:
        school_data_list.extend(
            output
        )  # ENROLMENT DATA IS IN DICT FORMAT NOT LIST OF DICT

    report_card_raw = scl_data.get_pandas_dataframe(
        school_data_list
    )  # Prints the dataframe shape

    return report_card_raw


@def_log.log_documentation_decorator
def main(id_list):
    REPORT_URLS = report_card_urls(id_list)
    REPORT_RAW_DATA = obtain_school_data(REPORT_URLS, DATA_SET)

    REPORT_RAW_DATA.to_csv(
        r"C:\Users\Sachit Deshmukh\Documents\Python Scripts\JPAL_UDISE_DATA_EXTRACTION\outputs\temp_2.csv"
    )

    return REPORT_RAW_DATA


if __name__ == "__main__":
    data: pd.DataFrame = (
        report_raw.main()
    )  # Ensures that the output from main() is a pandas DataFrame

    id_list = clean_id.main(data)

    main(id_list)
