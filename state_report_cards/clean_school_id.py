"""
THIS FILE WILL RETURN LIST OF SCHOOL IDS FOR RELEVANT SCHOOLS FOR MATH GAMES SCALE UP.
"""

# IMPORTING NECESSARY LIBRARIES
import pandas as pd
import udise_api_calls.init_logger as def_log  # ENSURE INSTALLATION OF JPALUDISE FOR ABSOLUTE IMPORT
import state_report_cards.state_school_data as report_raw
from state_report_cards import configuration as report_config

# DEFINING THE GLOBALS
LOGGER = def_log.main(__name__)


def drop_extra_columns(dataframe: pd.DataFrame, col_list: list) -> pd.DataFrame:
    raw_dataframe = dataframe
    cols_to_keep = col_list

    dropped_cols_dataframe = raw_dataframe[cols_to_keep]

    print(
        f"The dataframe after dropping columns is: {dropped_cols_dataframe.shape} in size."
    )

    return dropped_cols_dataframe


def correct_data_types(dataframe: pd.DataFrame, target_col: str) -> pd.DataFrame:
    """
    There is only 1 data type that is incorrect.
    It should be changed from float to int type.
    """
    target_col = target_col
    dataframe[target_col] = dataframe[target_col].astype(int)

    return dataframe


def filter_relevant_school_types(
    dataframe: pd.DataFrame, filter_values: dict
) -> pd.DataFrame:
    filter_values = filter_values
    data = dataframe
    filtered_data: pd.DataFrame = data.copy(deep=True)

    for column, values in filter_values.items():
        filtered_data = filtered_data[filtered_data[column].isin(values)]

    print(
        f"The dataframe after filtering school types is: {filtered_data.shape} in size."
    )

    return filtered_data


def obtain_school_ids(dataframe: pd.DataFrame) -> list:
    data = dataframe
    school_ids = data["schoolId"].tolist()

    print(f"The length of school ID list is: {len(school_ids)}.")

    return school_ids


@def_log.log_documentation_decorator
def main(dataframe: pd.DataFrame) -> list:
    """
    Cleans the data and outputs the school IDs of relevant schools for Math Games.

    Return
    ---
        List of school IDs.
    """
    try:
        # Dataframe does not have empty values in targer columns
        KEEP_COLS = report_config.COLS_TO_KEEP
        keep_data = drop_extra_columns(dataframe, KEEP_COLS)

        SCHOOL_TYPES = report_config.FILTER_SCHOOL_VALUES
        filter_data = filter_relevant_school_types(keep_data, SCHOOL_TYPES)

        SCHOOL_IDS = obtain_school_ids(filter_data)

        LOGGER.info(
            f"{len(SCHOOL_IDS)} school IDs of functional schools for state-district combination obtained."
        )

        return SCHOOL_IDS

    except Exception as e:
        LOGGER.debug(f"School IDs of functional school not obtained due to error: {e}")


if __name__ == "__main__":
    data: pd.DataFrame = (
        report_raw.main()
    )  # Ensures that the output from main() is a pandas DataFrame

    main(data)
