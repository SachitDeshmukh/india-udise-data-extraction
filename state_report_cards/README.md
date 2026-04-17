# State Report Cards

A Python-based pipeline that extracts state-specific school data from the [UDISE+ API](https://kys.udiseplus.gov.in/), filters for operational schools, and merges detailed report card data into a single analysis-ready dataset.

---

## Project Structure

| File | Description |
|---|---|
| `configuration.py` | Central config file for geographic scope and data filtering preferences |
| `state_school_data.py` | Fetches raw school data for configured state-district combinations |
| `clean_school_id.py` | Filters schools by type and status, extracts school IDs |
| `report_card_raw.py` | Fetches detailed enrollment and infrastructure data in parallel batches |
| `report_card_clean.py` | Extracts school IDs from API URLs and merges datasets |
| `main.py` | Entry point — orchestrates the entire pipeline and saves final data to CSV |

---

## Setup & Usage

### Prerequisites

| Package | Version | Purpose |
|---|---|---|
| `pandas` | 2.2.3+ | Data manipulation |
| `joblib` | 1.5.3+ | Parallel processing |
| `aiohttp` | 3.13.4+ | Async HTTP requests |
| `udise_api_calls` | Local | Core API and logging utilities |

### Run

```bash
uv run python state_report_cards\main.py
```

Output is saved to the parent directory captured in `OUTPUT_DIR` inside `udise_api_calls/configuration.py`, with filenames in the format:

```
UDISE_SCHOOL_DATA_YYYY-MM-DD_HH-MM-SS.csv
```

---

## Configuration (`configuration.py`)

All tunable settings live in one place — `configuration.py`. Edit this file to change geographic scope and filtering behavior without touching any pipeline logic.

| Parameter | Description |
|---|---|
| `STATE_ID_LIST` | State IDs to extract (currently `["127"]` for Maharashtra) |
| `DISTRICT_ID_LIST` | District IDs within the state (Akola, Jalna, Nashik, Ratnagiri, Wardha) |
| `COLS_TO_KEEP` | Columns retained from raw school data (e.g. schoolId, schoolName, districtName) |
| `FILTER_SCHOOL_VALUES` | School type and status filters (e.g. "Operational" only) |
| `API_DATA_SET_LEVEL_2` | Data field for enrollment data (`"schEnrollmentYearDataTotal"`) |
| `URL_COL` | DataFrame column containing API URLs (`"api_url"`) |
| `MERGE_COL` | Column to merge on (`"schoolId"`) |

---

## How It Works

The pipeline runs across four files in sequence, each feeding its output into the next. <b>The entry point is `main.py`.</b>

- `main.py` calls all downstream modules in order.
- `state_school_data.py` fetches raw school data for the configured state-district pairs.
- `clean_school_id.py` filters and cleans the school data, returning filtered schools and their IDs.
- `report_card_raw.py` uses those IDs to fetch detailed enrollment and infrastructure data.
- `report_card_clean.py` merges the two datasets and saves the result.

---

### Stage 1 — Fetch Raw School Data (`state_school_data.py`)

Create state-district ID pairs from configuration, generate API URLs, and fetch all schools in those districts.

```python
# In output_level_1_raw()
STATE_IDS = report_config.STATE_ID_LIST
DISTRICT_IDS = report_config.DISTRICT_ID_LIST

# Create all state-district combinations
ID_PAIRS = create_id_pairs(STATE_IDS, DISTRICT_IDS)

# Generate API URLs for each pair
URL_LIST = get_urls(ID_PAIRS)

# Fetch school data for all pairs
RAW_DATA = obtain_school_data(URL_LIST, DATA_SET)
```

The `ID_PAIRS` is a list of dictionaries like `{"stateID": "127", "districtID": "3705"}`. This avoids needing to cross-reference two separate lists later.

---

### Stage 2 — Filter Schools (`clean_school_id.py`)

From the raw school data, retain only the relevant columns, filter for operational schools, and extract school IDs.

```python
# In output_school_id_data()
KEEP_COLS = report_config.COLS_TO_KEEP
keep_data = drop_extra_columns(raw_dataframe, KEEP_COLS)

# Filter for operational schools
SCHOOL_TYPES = report_config.FILTER_SCHOOL_VALUES
filter_data = filter_relevant_school_types(keep_data, SCHOOL_TYPES)

# Extract school IDs as a list
SCHOOL_IDS = obtain_school_ids(filter_data)
```

The `FILTER_SCHOOL_VALUES` dictionary defines which school statuses and types to keep:

```python
FILTER_SCHOOL_VALUES = {
    "schoolStatusName": ["Operational", "DCF not Received", "Sanctioned but not Operational"],
    "schCatDesc": ["Primary", "Primary with Upper Primary", "Pr. Up Pr. and Secondary Only", ...]
}
```

This stage also converts the `schoolId` column from float to int to ensure compatibility in later merges.

Returns two outputs:
- `SCHOOL_IDS` — list of integer school IDs for operational schools only
- `filter_data` — filtered DataFrame with relevant columns and schools

---

### Stage 3 — Fetch Report Card Data (`report_card_raw.py`)

For each school ID from Stage 2, generate an API URL that returns detailed enrollment and infrastructure data.

```python
# In output_level_2_raw()
REPORT_URLS = report_card_urls(id_list)  # Generate individual school URLs

# Fetch in parallel batches
REPORT_RAW_DATA = obtain_school_data(REPORT_URLS, DATA_SET)
```

The `report_card_urls()` function generates URLs in the format:

```
https://kys.udiseplus.gov.in/webapp/api/getSocialData?flag=1&schoolId=<ID>&yearId=11
```

These are then batched and processed in parallel (similar to the main extraction pipeline) to collect enrollment totals by class and gender.

---

### Stage 4 — Merge Datasets (`report_card_clean.py`)

Extract school IDs from the report card API URLs, add them as a new column, and merge with the filtered school data.

```python
# In output_clean_data()
# Extract schoolId from API URLs
LEVEL_2_CLEAN = add_school_id_to_data(LEVEL_2_RAW, report_config.URL_COL)

# Merge on schoolId
COL_NAME = report_config.MERGE_COL
CLEAN_DATA = merge_dataframes(LEVEL_1_CLEAN, LEVEL_2_CLEAN, COL_NAME)
```

The `extract_school_id()` function parses the URL query string to retrieve the `schoolId` parameter:

```python
def extract_school_id(url: str) -> int:
    parsed = urlparse(url)
    query = parsed.query
    params = parse_qs(query)
    school_id_list = params.get("schoolId", [None])
    school_id = int(school_id_list[0])
    return school_id
```

The final merge combines school metadata (name, district, type) with enrollment data (grade-wise totals) into a single DataFrame ready for analysis.
