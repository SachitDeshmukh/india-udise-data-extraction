# Importing all necessary libraries

import pandas as pd
import asyncio
import logging
import os
from joblib import Parallel, delayed
from udise_api_calls import api_config
from udise_api_calls import def_log_main, def_log_dec
from udise_api_calls import api_url_call, api_url_main


def yield_url_batches(url_list: list):
    url_chunks = api_config.URL_CHUNKS
    url_list = url_list

    for i in range(0, len(url_list), url_chunks):
        yield url_list[i : i + url_chunks]


async def single_get_call(url: str, data_set: str, logger: logging.Logger):
    """
    Fetch and extract school data for a single URL.
    """
    try:
        python_output = await api_url_call(url)
        school_data = python_output["data"][data_set]
        if type(school_data) == list:  # LIST OF DICTIONARIES
            for data in school_data:
                data["api_url"] = url
            return school_data
        elif type(school_data) == dict:
            school_data["api_url"] = url
            return school_data
        else:
            logger.debug("Output data from API call is neither a list or a dictionary.")
            return school_data
    except Exception as e:
        logger.debug(f"No school data found for url: {url} due to error: {e}")


async def async_fire_api(url_batch: list, data_set: str) -> list:
    """
    Fire all URLs in a batch concurrently to obtain response from API calls.
    """
    # SET UP LOGGING - unique per worker process
    worker_id = os.getpid()
    logger_name = f"{__name__}.worker_{worker_id}"
    LOGGER = logging.getLogger(logger_name)

    # PREVENT DUPLICATE PROCESSEES IF HANDDLER ALREADY EXITS
    if not LOGGER.handlers:
        LOGGER = def_log_main(logger_name)

    all_school_data = []

    semaphore = asyncio.Semaphore(
        api_config.CALL_LIMIT
    )  # limit the max no of concurrent calls per worker

    async def limit_get_calls(url, data_set, LOGGER):
        async with semaphore:  # blocks here if max limit of calls already in-flight
            return await single_get_call(url, data_set, LOGGER)

    tasks = [limit_get_calls(url, data_set, LOGGER) for url in url_batch]
    results = await asyncio.gather(*tasks)  # all URLs fired concurrently

    for result in results:
        if type(result) == list:
            all_school_data.extend(result)  # WHEN CONTENT = LIST OF DICT
        if type(result) == dict:
            all_school_data.append(result)  # WHEN ENROLL_DATA = DICT

    LOGGER.info(
        f"[PID {worker_id}] Batch complete. {len(all_school_data)} records extracted."
    )
    return all_school_data


def obtain_school_data(url_batch: str, data_set) -> list:
    """
    Sync wrapper so joblib can call this from each worker process.
    """
    loop = asyncio.new_event_loop()  # create a brand new event loop
    asyncio.set_event_loop(loop)  # set it as the current loop
    try:
        return loop.run_until_complete(async_fire_api(url_batch, data_set))
    finally:
        loop.close()  # clean up after batch is done


def get_pandas_dataframe(data: list) -> pd.DataFrame:
    raw_data = data
    final_data = pd.DataFrame(raw_data)

    print(final_data.shape)

    return final_data


@def_log_dec
def main():
    """
    1. Generate list of URL batches for parsing through parallel workers.
    2. Obtain school data for each batch of urls parallely.
    3. Convert entire data set of school data into Pandas DataFrame.
    """

    # STEP 1
    API_URL_LIST = api_url_main()
    URL_BATCHES = list(yield_url_batches(API_URL_LIST))
    DATA_SET = api_config.API_DATA_SET_LEVEL_1

    # print(URL_BATCHES)

    # STEP 2
    all_school_data_list = []
    parallel_output = Parallel(
        n_jobs=api_config.PARALLEL_JOBS, backend="multiprocessing"
    )(delayed(obtain_school_data)(url_batch, DATA_SET) for url_batch in URL_BATCHES)
    for output in parallel_output:
        all_school_data_list.extend(output)

    # print(all_school_data_list)

    # STEP 3
    all_school_data = get_pandas_dataframe(all_school_data_list)

    # print(all_school_data.head(10))

    return all_school_data


if __name__ == "__main__":
    LOGGER = def_log_main(__name__)
    main()
