# UDISE Data Pipeline

A Python-based pipeline for fetching and processing school data from the UDISE (Unified District Information System for Education) API.

> **Note:** This repository contains two modules — currently the API calls module has a README with detailed documentation.
> - [`udise_api_calls/`](./udise_api_calls/README.md) — Handles API requests to the UDISE portal and extracts JSON data for each school
> - [`udise_data_scrapper/`](./udise_data_scrapper/README.md) — Wrok-in-progress: Scrapes data using Selenium browser.

---

## Prerequisites

- Python 3.8+
- pip

---

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Refer to the README in the sub-module for specific run instructions:

- For API calls → [`udise_api_calls/`](./udise_api_calls/README.md)

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `selenium` | 4.18.1 | Browser automation |
| `pandas` | 2.2.3 | Data manipulation |
| `joblib` | 1.5.3 | Parallel processing |
| `requests` | 2.32.5 | HTTP / API calls |

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.