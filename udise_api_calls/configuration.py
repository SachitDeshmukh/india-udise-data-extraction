# NOTING ALL CONFIG SETTING HERE
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_PATH = PROJECT_ROOT / "logs"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
# Create them if they don't exist
LOGS_PATH.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

UDISE_API_BASE_URL = "https://kys.udiseplus.gov.in/web-app/api/"
API_RETRIES = 5
API_TIMEOUT = 15  # 15 SECONDS
URL_CHUNKS = 100
CALL_LIMIT = 10
PARALLEL_JOBS = 6
EXCEL_FILE_BASE_TEXT = "UDISE_SCHOOL_DATA"
API_DATA_SET_LEVEL_1 = "content"
