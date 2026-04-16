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
from .get_all_api_url import main as api_url_main

# IMPORTING FUNCTIONS TO FIRE GET CALLS IN PARALLEL BATCHES
from .obtain_school_data import main as scl_data_main

# IMPORTING FUNCTIONS TO SAVE OUTPUT IN CSV
from .save_file import save_data_to_file as save_csv

__all__ = [
    "api_config",
    "def_log_main",
    "def_log_dec",
    "api_url_call",
    "api_url_main",
    "scl_data_main",
    "save_csv",
]
