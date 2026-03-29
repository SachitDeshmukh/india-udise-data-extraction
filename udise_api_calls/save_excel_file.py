# Importing all necessary libraries

import pandas as pd
from datetime import datetime

from udise_api_calls import init_logger
from udise_api_calls import configuration as api_config
from udise_api_calls import obtain_school_data


# Defining GLOBALS
FILE_NAME_BASE = api_config.EXCEL_FILE_BASE_TEXT
OUTPUT_DIR = r"C:\Users\Sachit Deshmukh\Documents\Python Scripts\JPAL_UDISE_DATA_EXTRACTION\outputs"
LOGGER = init_logger.main(__name__)


def save_data_to_file(data: pd.DataFrame):
    version_date = str(f"{datetime.now().strftime('%Y-%m-%d')}")
    version_time = str(f"{datetime.now().strftime("%H-%M-%S")}")
    data_frame = data

    try:
        csv_file_path = str(
            OUTPUT_DIR + f"/{FILE_NAME_BASE}_{version_date}_{version_time}.csv"
        )
        data_frame.to_csv(csv_file_path)
        LOGGER.info(f"All school level data has been saved to file: {csv_file_path}")

    except Exception as e:
        LOGGER.debug(f"Data was not saved due to error: {e}")


@init_logger.log_documentation_decorator
def main():
    all_data = obtain_school_data.main()
    save_data_to_file(all_data)


if __name__ == "__main__":
    main()
