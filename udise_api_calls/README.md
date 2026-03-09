# UDISE School Data Scraper

A Python-based pipeline that fetches school-level data from the [UDISE+ API](https://kys.udiseplus.gov.in/) across all Indian states and districts, and saves the results to a CSV file.

---

## Project Structure

| File | Description |
|---|---|
| `configuration.py` | Central config file for API settings and output preferences |
| `get_all_api_url.py` | Fetches state and district IDs from the API and builds a list of request URLs |
| `obtain_school_data.py` | Fetches school data in parallel batches and returns a Pandas DataFrame |
| `save_excel_file.py` | Entry point — saves the final DataFrame to a timestamped CSV file |

---

## Setup & Usage

### Prerequisites

```bash
pip install requests pandas joblib openpyxl
```

### Run

```bash
python save_excel_file.py
```

Output is saved to the directory defined in `OUTPUT_DIR` inside `save_excel_file.py`, with filenames in the format:

```
UDISE_SCHOOL_DATA_YYYY-MM-DD_HH-MM-SS.csv
```

> **Note:** Update the `OUTPUT_DIR` path in `save_excel_file.py` to match your local environment before running.

---

## Configuration (`configuration.py`)

All tunable settings live in one place — `configuration.py`. Edit this file to change behaviour without touching any pipeline logic.

```python
UDISE_API_BASE_URL = "https://kys.udiseplus.gov.in/webapp/api/"
API_RETRIES = 5
URL_CHUNKS = 100
PARALLEL_JOBS = 6
EXCEL_FILE_BASE_TEXT = "UDISE_SCHOOL_DATA"
```

| Parameter | Default | Description |
|---|---|---|
| `UDISE_API_BASE_URL` | UDISE+ API base | Base URL for all API calls |
| `API_RETRIES` | `5` | Number of retry attempts on failed requests |
| `URL_CHUNKS` | `100` | Number of URLs processed per parallel batch |
| `PARALLEL_JOBS` | `6` | Number of parallel workers |
| `EXCEL_FILE_BASE_TEXT` | `UDISE_SCHOOL_DATA` | Prefix for the output filename |

---

## How It Works

The pipeline runs across three files in sequence, each feeding its output into the next. The entry point is `save_excel_file.py`, which calls `obtain_school_data.py`, which in turn calls `get_all_api_url.py`.

---

### Step 1 — Fetch All State IDs (`get_all_api_url.py`)

The pipeline starts by calling the UDISE+ API to get a list of all Indian states.

```python
# In get_all_api_url.main()
state_api_url = BASE_URL + "states?&yearId=0"
state_ids = get_state_ids(state_api_url)
```

`get_state_ids()` makes a GET request and pulls the `stateId` field out of each entry in the response:

```python
def get_state_ids(call_url: str) -> list:
    json_output = make_get_call(target_url=call_url)
    states_data: list = json_output.json()["data"]

    all_state_ids = []
    for state_data in states_data:
        state_id_temp = str(state_data["stateId"])
        all_state_ids.append(state_id_temp)

    return all_state_ids  # e.g. ["1", "2", "3", ...]
```

---

### Step 2 — Fetch All District IDs (`get_all_api_url.py`)

For every state ID retrieved above, the pipeline makes another API call to get all districts within that state.

```python
# In get_district_ids()
for ID in state_IDs:
    temp_district_url = BASE_URL + f"districts?stateId={ID}&yearId=0"
    temp_python_output = make_get_call(target_url=temp_district_url).json()

    for district_data in temp_python_output["data"]:
        state_district_data.append({
            "stateID": ID,
            "districtID": district_data["districtId"]
        })
```

Each state-district pair is stored as a dictionary, e.g. `{"stateID": "7", "districtID": "42"}`. This avoids needing to cross-reference two separate lists later on.

---

### Step 3 — Build API URLs for Every State-District Pair (`get_all_api_url.py`)

With all state-district pairs in hand, the pipeline constructs one API request URL per pair — these are the URLs that will actually return school-level data.

```python
# In state_districts_urls()
for pair_entry in ID_pairs:
    stateID = pair_entry["stateID"]
    districtID = pair_entry["districtID"]
    temp_school_data_url = BASE_URL + f"search-school/by-region?stateId={stateID}&districtId={districtID}"
    all_call_urls.append(temp_school_data_url)
```

The result is a flat list of URLs — one per district — ready to be batched and fetched.

---

### Step 4 — Fetch School Data in Parallel Batches (`obtain_school_data.py`)

Rather than calling each URL one at a time, the pipeline splits the full URL list into batches of 100 (configurable via `URL_CHUNKS`) and processes them in parallel using `joblib`.

**Batching the URLs:**
```python
def yield_url_batches(url_list: list):
    url_chunks = configuration.URL_CHUNKS  # default: 100

    for i in range(0, len(url_list), url_chunks):
        yield url_list[i : i + url_chunks]
```

**Running batches in parallel:**
```python
parallel_output = Parallel(n_jobs=configuration.PARALLEL_JOBS, backend="multiprocessing")(
    delayed(obtain_school_data)(url_batch) for url_batch in URL_BATCHES
)
```

Each worker runs `obtain_school_data()`, which iterates through its assigned URLs and collects every school entry from the API response:

```python
def obtain_school_data(url_batch: str) -> list:
    all_school_data = []
    for url in url_batch:
        json_output = get_all_api_url.make_get_call(url)
        school_data_entries: list = json_output.json()["data"]["content"]
        for entry in school_data_entries:
            all_school_data.append(entry)
    return all_school_data
```

Once all workers finish, their results are merged into a single list and converted to a Pandas DataFrame.

---

### Step 5 — Save to CSV (`save_excel_file.py`)

The final DataFrame is saved to a timestamped CSV file in the configured output directory.

```python
def save_data_to_file(data: pd.DataFrame):
    version_control = datetime.now().strftime('%Y-%m-%d')
    sheet_name = datetime.now().strftime("%H-%M-%S")

    csv_file_path = OUTPUT_DIR + f"/{FILE_NAME_BASE}_{version_control}_{sheet_name}.csv"
    data_frame.to_csv(csv_file_path)
```

The timestamp in the filename ensures previous runs are never overwritten, making it easy to track data pulls over time.

---

## Error Handling & Retries

All API calls go through the `make_get_call()` function in `get_all_api_url.py`, which handles transient failures gracefully with automatic retries and a 5-second wait between attempts.

```python
def make_get_call(target_url: str, retries=API_RETRIES):
    for connection_attempt in range(retries):
        try:
            api_session = requests.session()
            call_response = api_session.get(url=target_url, timeout=(5, 15))
            call_response.raise_for_status()
            return call_response

        except requests.exceptions.ConnectTimeout:
            logging.error(f"Timeout. Retry {connection_attempt+1}/{retries}")
            wait_for_next_requests_session()  # sleeps 5 seconds

        except requests.exceptions.ConnectionError:
            logging.error(f"Connection error. Retry {connection_attempt+1}/{retries}")
            wait_for_next_requests_session()

        except requests.exceptions.HTTPError:
            logging.error(f"HTTP error. Retry {connection_attempt+1}/{retries}")
            wait_for_next_requests_session()

    raise Exception("API failed after retries")
```

The three caught exceptions cover the most common failure scenarios:
- **`ConnectTimeout`** — the server took too long to respond
- **`ConnectionError`** — a network-level failure (e.g. DNS, dropped connection)
- **`HTTPError`** — the server responded with a 4xx or 5xx status code

If all retries are exhausted, an exception is raised and logged. For school data batches specifically, the error is caught without stopping the rest of the pipeline — partial data is still returned.

---

## Logging

All three pipeline files use Python's `logging` module at `INFO` level, so you can follow progress in the console as the scraper runs. Key log messages include:

- State ID extraction complete
- All district-level URLs generated
- Each URL batch successfully processed
- Final CSV file path on save