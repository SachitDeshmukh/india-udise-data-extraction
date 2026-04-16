# UDISE+ API Calls

A Python-based pipeline that fetches school-level data from the [UDISE+ API](https://kys.udiseplus.gov.in/) across all Indian states and districts, and saves the results to a CSV file.

---

## Project Structure

| File | Description |
|---|---|
| `configuration.py` | Central config file for API settings and output preferences |
| `init_logger.py` | Configuration for logging — initializes loggers to segregate logs |
| `get_all_api_url.py` | Fetches state and district IDs from the API and builds a list of "get" URLs |
| `obtain_school_data.py` | Fetches school data in parallel batches and returns a Pandas DataFrame |
| `save_file.py` | Entry point — runs all processes and saves the final DataFrame to a timestamped CSV file |

---

## Setup & Usage

### Prerequisites

| Package | Version | Purpose |
|---|---|---|
| `pandas` | 2.2.3+ | Data manipulation |
| `joblib` | 1.5.3+ | Parallel processing |
| `aiohttp` | 3.13.4+ | Async HTTP requests |

### Run

```bash
uv run python -m udise_api_calls\save_file.py
```

Output is saved to the parent directory captured in `OUTPUT_DIR` inside `configuration.py`, with filenames in the format:

```
UDISE_SCHOOL_DATA_YYYY-MM-DD_HH-MM-SS.csv
```

---

## Configuration (`configuration.py`)

All tunable settings live in one place — `configuration.py`. Edit this file to change behaviour without touching any pipeline logic.

| Parameter | Default | Description |
|---|---|---|
| `UDISE_API_BASE_URL` | `"https://kys.udiseplus.gov.in/webapp/api/"` | Base URL for all get calls |
| `API_RETRIES` | `5` | Number of retry attempts on failed get calls |
| `API_TIMEOUT` | `15` | Total timeout in seconds for each call |
| `URL_CHUNKS` | `100` | Number of URLs processed per worker in parallel processing |
| `CALL_LIMIT` | `10` | Maximum concurrent get calls per worker during asynchronous execution |
| `PARALLEL_JOBS` | `6` | Number of parallel workers |
| `EXCEL_FILE_BASE_TEXT` | `"UDISE_SCHOOL_DATA` | Prefix for the output filename |
| `API_DATA_SET_LEVEL_1` | `"content"` | Data field extracted from each get calls response |
---

## How It Works

The pipeline runs across three files in sequence, each feeding its output into the next. <b>The entry point is `save_file.py`.</b>
- The `main` function calls `obtain_school_data.py` to fire concurrent get calls in parallel batches and returns a Pandas Dataframe.
- The `obtain_school_data.py` module calls `get_all_api_url.py` to obtain all the get URLs for each school from the UDISE+ Know Your School portal.

---

### Step 1 — Fetch All State IDs (`get_all_api_url.py`)

The pipeline starts by calling the UDISE+ API to get a list of all Indian states.

```python
# In get_all_api_url.main()
state_api_url = BASE_URL + "states?&yearId=0"
state_ids = get_state_ids(state_api_url)
```

`get_state_ids()` makes an async GET request and pulls the `stateId` field out of each entry in the response:

```python
def get_state_ids(call_url: str) -> list:
    python_output = asyncio.run(make_get_call(target_url=call_url))
    states_data: list = python_output["data"]

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
    temp_python_output = asyncio.run(make_get_call(target_url=temp_district_url))

    for district_data in temp_python_output["data"]:
        state_district_data.append({
            "stateID": ID,
            "districtID": district_data["districtId"]
        })
```

Each state-district pair is stored as a dictionary, e.g. `{"stateID": "7", "districtID": "42"}`. This avoids needing to cross-reference two separate lists later when creating get URLs for school data in step 3.

---

### Step 3 — Build API URLs for Every State-District Pair (`get_all_api_url.py`)

With all state-district pairs in hand, the pipeline constructs one get request URL per pair — these are the URLs that will actually return school-level data.

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
    url_chunks = api_config.URL_CHUNKS

    for i in range(0, len(url_list), url_chunks):
        yield url_list[i : i + url_chunks]
```

**Running batches in parallel:**
```python
parallel_output = Parallel(
    n_jobs=api_config.PARALLEL_JOBS, backend="multiprocessing"
)(delayed(obtain_school_data)(url_batch, DATA_SET) for url_batch in URL_BATCHES)
```

Each worker runs `obtain_school_data()`, which uses `asyncio` inside the worker process to fire the URLs in the batch concurrently and collect school entries from the API responses.

```python
async def single_get_call(url, data_set, logger):
    try:
        python_output = await get_all_api_url.make_get_call(url)
        school_data = python_output["data"][data_set]
        if type(school_data) == list:
            for data in school_data:
                data["api_url"] = url
            return school_data
        elif type(school_data) == dict:
            school_data["api_url"] = url
            return school_data
        else:
            logger.debug("Output data from API call is neither a list or a dictionary.")
            return school_data
    except Exception as e:
        logger.debug(f"No school data found for url: {url} due to error: {e}")
```

The code also annotates each returned record with `api_url`, so you can trace which district call produced it. Once all workers finish, their results are merged into a single list and converted to a Pandas DataFrame.

---

### Step 5 — Save to CSV (`save_file.py`)

The final DataFrame is saved to a timestamped CSV file in the configured output directory.

```python
def save_data_to_file(data: pd.DataFrame):
    version_date = datetime.now().strftime('%Y-%m-%d')
    version_time = datetime.now().strftime('%H-%M-%S')

    csv_file_path = OUTPUT_DIR / f"{FILE_NAME_BASE}_{version_date}_{version_time}.csv"
    data_frame.to_csv(csv_file_path)
```

The timestamp in the filename ensures previous runs are never overwritten, making it easy to track data pulls over time.

---

## Error Handling & Retries

All API calls go through the `make_get_call()` function in `get_all_api_url.py`, which handles transient failures gracefully with automatic retries and a 5-second wait between attempts.

```python
async def wait_for_attempt():
    await asyncio.sleep(5)

async def make_get_call(target_url: str, retries=API_RETRIES):
    for connection_attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as api_session:
                async with api_session.get(
                    url=target_url, timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
                ) as call_response:
                    call_response.raise_for_status()
                    json_data = await call_response.json()
                    return json_data

        except aiohttp.ServerTimeoutError:
            LOGGER.warning(
                f"Connection timeout. Retry {connection_attempt+1}/{retries}"
            )
            await wait_for_attempt()

        except asyncio.TimeoutError:
            LOGGER.warning(f"Read timeout. Retry {connection_attempt+1}/{retries}")
            await wait_for_attempt()

        except aiohttp.ClientConnectionError:
            LOGGER.warning(f"Connection error. Retry {connection_attempt+1}/{retries}")
            await wait_for_attempt()

        except aiohttp.ClientResponseError:
            LOGGER.warning(f"HTTP error. Retry {connection_attempt+1}/{retries}")
            await wait_for_attempt()

    raise Exception("API failed after retries")
```

The four caught exceptions cover the most common failure scenarios:
- **`ServerTimeoutError`** — the server took too long to respond
- **`TimeoutError`** — the request read timed out
- **`ClientConnectionError`** — a network-level failure (e.g. DNS, dropped connection)
- **`ClientResponseError`** — the server responded with a 4xx or 5xx status code

If all retries are exhausted, an exception is raised and logged. For school data batches specifically, the error is caught without stopping the rest of the pipeline — partial data is still returned.

---

## Logging

Logging is configured at `DEBUG` level across the pipeline. `INFO` and `DEBUG` messages are written to `logs/info.log` and `logs/debug.log` respectively, while `WARNING` and higher-level messages are emitted to the console.

Key log messages include:

- State ID extraction complete
- All district-level URLs generated
- Each URL batch successfully processed
- Final CSV file path on save

Key debug messages include:

- Output data from API call is neither a list or a dictionary.
- No school data found for url.
- Data was not saved due to error.