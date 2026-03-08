# Importing all necessary libraries

import json
import pandas as pd
from joblib import Parallel, delayed
import logging
import configuration
import get_all_api_url

# Set logging format and level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Defining the GLOBALS
API_URL_LIST = get_all_api_url.main()


def yield_url_batches(url_list: list):
    url_chunks = configuration.URL_CHUNKS
    url_list = url_list

    for i in range(0, len(url_list), url_chunks):
        yield url_list[i : i + url_chunks]


def obtain_school_data_json(call_url: str) -> json:
    pass


def main():
    """
    1. Generate list of URL batches for parsing through parallel workers.
    2. Obtain school data for each batch of urls parallely.
    3. Convert entire data set of school data into Pandas DataFrame.
    """

    # STEP 1
    URL_BATCHES = list(yield_url_batches(API_URL_LIST))

    # print(URL_BATCHES)


if __name__ == "__main__":
    main()
