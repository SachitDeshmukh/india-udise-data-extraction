# UDISE Data Pipeline

A Python repository for extracting and processing school data from the UDISE+ API.

This repository contains multiple independent Python packages, each with its own runnable entry point:

- `udise_api_calls/` — API extraction package for fetching school data and saving it to CSV.
- `udise_data_scrapper/` — Selenium-based scraper package for browser-driven data extraction.
- `state_report_cards/` — state-level reporting utilities and data cleaning helpers.

Each package is structured as a standalone Python package and can be executed independently from the repository root.

---

## Repository Structure

- `pyproject.toml` — package metadata and dependency definitions.
- `README.md` — repository overview.
- `udise_api_calls/` — API extraction package with its own documentation.
- `udise_data_scrapper/` — browser scraper package.
- `state_report_cards/` — report card and data cleaning utilities.
- `backend_resources/`, `logs/`, `outputs/` — helper resources and runtime output directories.

---

## Prerequisites

- uv

---

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/SachitDeshmukh/india-udise-data-extraction
   ```

2. Install dependencies using `uv` and `pyproject.toml`:
   ```bash
   uv sync
   ```

3. Run necessary modules using `uv`:
   ```bash
   uv run python -m <module-name>
   ```

## Usage

Refer to the README in the sub-module for specific run instructions:

- For UDISE API calls → [`udise_api_calls/`](./udise_api_calls/README.md)

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `selenium` | 4.18.1+ | Browser automation |
| `pandas` | 2.2.3+ | Data manipulation |
| `joblib` | 1.5.3+ | Parallel processing |
| `requests` | 2.32.5+ | HTTP / API calls |
| `aiohttp` | 3.13.4+ | Async HTTP requests |

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.