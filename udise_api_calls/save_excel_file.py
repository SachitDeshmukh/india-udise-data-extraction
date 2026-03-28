# Importing all necessary libraries

import pandas as pd
from datetime import datetime
import init_logger

import configuration
import obtain_school_data


# Defining GLOBALS
FILE_NAME_BASE = configuration.EXCEL_FILE_BASE_TEXT
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


def main():
    all_data = obtain_school_data.main()
    save_data_to_file(all_data)


if __name__ == "__main__":
    LOGGER.info(f"Running the code: {__file__}") # FOR DOCUMENTATION
    LOGGER.debug(f"Running the code: {__file__}") # FOR DOCUMENTATION

    main()

    LOGGER.info("Run complete.")
    LOGGER.debug("Run complete.")
