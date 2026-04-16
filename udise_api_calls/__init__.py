"""
THIS MODULE STORES API RESPONSE DATA INTO CSV FILES.
"""

# # IMPORTING CONFIG FILE
from . import configuration as api_config

# IMPORTING CUSTOM LOGGING MODULE
from .init_logger import log_documentation_decorator as def_log_dec
from .init_logger import main as def_log_main

# IMPORTING FUNCTIONS TO MAKE API GET CALLS
from .get_all_api_url import make_get_call as api_url_call
from .get_all_api_url import state_districts_urls as api_url_pair
from .get_all_api_url import main as api_url_main

# IMPORTING FUNCTIONS TO FIRE GET CALLS IN PARALLEL BATCHES
from .obtain_school_data import main as scl_data_main
from .obtain_school_data import obtain_school_data as scl_data_obtain
from .obtain_school_data import yield_url_batches as scl_data_yield
from .obtain_school_data import get_pandas_dataframe as scl_data_frame

# IMPORTING FUNCTIONS TO SAVE OUTPUT IN CSV
from .save_file import save_data_to_file as save_csv

__all__ = [
    "api_config",
    "def_log_main",
    "def_log_dec",
    "api_url_call",
    "api_url_pair",
    "api_url_main",
    "scl_data_main",
    "scl_data_obtain",
    "scl_data_yield",
    "scl_data_frame",
    "save_csv",
]
