"""
THIS IS THE ENTRY POINT TO CODE FOR EXTRACTING STATE SPECIFIC REPORT CARD DATA.
"""

# IMPORTING ALL NECESSARY LIBRARIES

from udise_api_calls import *
from state_report_cards import configuration as report_config
import state_report_cards.state_school_data as report_level_1
import state_report_cards.clean_school_id as clean_id
import state_report_cards.report_card_raw as report_level_2
import state_report_cards.report_card_clean as report_clean_csv


@def_log_dec
def main():
    LEVEL_1_RAW = report_level_1.output_level_1_raw()
    ID_LIST, LEVEL_1_CLEAN = clean_id.output_school_id_data(LEVEL_1_RAW)

    LEVEL_2_RAW = report_level_2.output_level_2_raw(ID_LIST)
    URL_COL = report_config.URL_COL
    LEVEL_2_CLEAN = report_clean_csv.add_school_id_to_data(LEVEL_2_RAW, URL_COL)

    COL_NAME = report_config.MERGE_COL
    CLEAN_DATA = report_clean_csv.output_clean_data(
        LEVEL_1_CLEAN, LEVEL_2_CLEAN, COL_NAME
    )
    save_csv(CLEAN_DATA)


if __name__ == "__main__":
    LOGGER = def_log_main(__name__)
    main()
