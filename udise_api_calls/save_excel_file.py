# Importing all necessary libraries

import pandas as pd
import os
from datetime import datetime
import logging

import configuration
import obtain_school_data

# Set logging format and level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Defining GLOBALS
FILE_NAME_BASE = configuration.EXCEL_FILE_BASE_TEXT
OUTPUT_DIR = r"C:\Users\Sachit Deshmukh\Documents\Python Scripts\JPAL_UDISE_DATA_EXTRACTION\outputs"


def save_data_to_file(data: pd.DataFrame):
    version_control = str(f"{datetime.now().strftime('%Y-%m-%d')}")
    sheet_name = str(f"{datetime.now().strftime("%H-%M-%S")}")
    data_frame = data

    try:
        csv_file_path = str(
            OUTPUT_DIR + f"/{FILE_NAME_BASE}_{version_control}_{sheet_name}.csv"
        )
        # Keeping a Back UP
        data_frame.to_csv(csv_file_path)

        # xlsx_file_path = str(OUTPUT_DIR + f"/{FILE_NAME_BASE}_{version_control}.xlsx")

        # mode = "a" if os.path.exists(xlsx_file_path) else "w"
        # with pd.ExcelWriter(xlsx_file_path, mode=mode, engine="openpyxl") as writer:
        #     data_frame.to_excel(writer, sheet_name=sheet_name, index=False)

        logging.info(f"All school level data has been saved to file: {csv_file_path}")

    except Exception as e:
        logging.error(f"Data was not saved due to error: {e}")


def main():
    all_data = obtain_school_data.main()
    save_data_to_file(all_data)


if __name__ == "__main__":
    main()
