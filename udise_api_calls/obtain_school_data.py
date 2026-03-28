# Importing all necessary libraries

import pandas as pd
from joblib import Parallel, delayed
from udise_api_calls import init_logger
from udise_api_calls import configuration as api_config
from udise_api_calls import get_all_api_url
import time


def wait_for_next_url():
    time.sleep(1)


def yield_url_batches(url_list: list):
    url_chunks = api_config.URL_CHUNKS
    url_list = url_list

    for i in range(0, len(url_list), url_chunks):
        yield url_list[i : i + url_chunks]


def obtain_school_data(url_batch: str) -> list:
    """
    Obtain all school level data in dictionary format.

    Return
        List of all school level data.
    """
    # SET UP LOGGING
    LOGGER = init_logger.main(__name__)

    all_school_data = []

    url_list = url_batch

    try:
        for url in url_list:
            json_output = get_all_api_url.make_get_call(url)
            python_output = json_output.json()

            # python_str = json.dumps(python_output, indent=2)
            # print(python_str)

            school_data_entries: list = python_output["data"]["content"]
            for entry in school_data_entries:
                # print(entry)
                all_school_data.append(entry)

        LOGGER.info(f"All school data for current URL batch has been extracted.")

    except Exception as e:
        LOGGER.debug(f"No school data found for this url: {url} due to error: {e}")

    finally:
        return all_school_data


def get_pandas_dataframe(data: list) -> pd.DataFrame:
    raw_data = data
    final_data = pd.DataFrame(raw_data)

    print(final_data.shape)

    return final_data


def main():
    """
    1. Generate list of URL batches for parsing through parallel workers.
    2. Obtain school data for each batch of urls parallely.
    3. Convert entire data set of school data into Pandas DataFrame.
    """

    # STEP 1
    API_URL_LIST = get_all_api_url.main()
    URL_BATCHES = list(yield_url_batches(API_URL_LIST))

    # print(URL_BATCHES)

    # STEP 2
    all_school_data_list = []
    parallel_output = Parallel(
        n_jobs=api_config.PARALLEL_JOBS, backend="multiprocessing"
    )(delayed(obtain_school_data)(url_batch) for url_batch in URL_BATCHES)
    for output in parallel_output:
        all_school_data_list.extend(output)

    # print(all_school_data_list)

    # STEP 3
    all_school_data = get_pandas_dataframe(all_school_data_list)

    # print(all_school_data.head(10))

    return all_school_data


if __name__ == "__main__":
    LOGGER = init_logger.main(__name__)
    LOGGER.info(f"Running the code: {__file__}")  # FOR DOCUMENTATION
    LOGGER.debug(f"Running the code: {__file__}")  # FOR DOCUMENTATION

    main()

    LOGGER.info("Run complete.")
    LOGGER.debug("Run complete.")
