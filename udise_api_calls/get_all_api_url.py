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
    request_url = httpResponse.url
    request_message = httpResponse.json()
    (
        logging.info(
            f"Request status: {request_message["status"]} for Request: {request_url}"
        )
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

    return call_response


def get_state_ids(call_url: str) -> list:
    """
    Makes API GET call and extracts schools IDs from JSON response.

    Returns:
        List of school IDs to iter over.
    """
    json_output = make_get_call(target_url=call_url)
    python_output = json_output.json()
    # Obtained request output data in Python disctionary format

    # state_data_formatted = json.dumps(python_output, indent=4)
    # print(state_data_formatted)

    states_data: list = python_output["data"]  # List of states data dictionaries

    all_state_ids = []

    for state_data in states_data:
        state_id_temp = str(state_data["stateId"])
        all_state_ids.append(state_id_temp)

    # print(all_state_ids)

    logging.info(
        f"State ID data from API call response for url: {call_url} successfully extracted"
    )

    return all_state_ids


def main():
    """
    1. Define the first API GET call url
    2. Place the API GET call for state Ids
    3. Create state-wise API GET calls for all district Ids
    4. Create state-district pairs of Ids
    5. Prepare a list of API GET call urls for each state-district pair
    """

    # STEP 1
    state_api_url_addition: str = "states?&yearId=0"
    state_api_url = str(BASE_URL + state_api_url_addition)

    # STEP 2
    state_ids = get_state_ids(state_api_url)


if __name__ == "__main__":
    main()
