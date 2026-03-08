# Importing all necessary libraries

import requests
import json
import logging
import configuration

# Set logging format and level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Defining the GLOBALS

BASE_URL: str = configuration.UDISE_API_BASE_URL


def check_call_status(httpResponse: requests.Response):
    request_message = httpResponse.json()
    (
        logging.info(f"Request status: {request_message["status"]}")
        if httpResponse.status_code == 200
        else logging.info(httpResponse)
    )


def make_get_call(target_url: str):
    """
    Makes GET API call.
    """
    api_session = requests.session()  # Initiate the API session

    try:
        call_response = api_session.get(url=target_url)
        call_response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise e
    except requests.exceptions.HTTPError as e:
        raise e

    check_call_status(call_response)


def main():
    trial_url = str(BASE_URL + "states?")
    make_get_call(trial_url)


if __name__ == "__main__":
    main()
