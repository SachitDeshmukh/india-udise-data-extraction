# Importing all necessary libraries

import requests
import time
from udise_api_calls import init_logger
from udise_api_calls import configuration as api_config

# Defining the GLOBALS
BASE_URL: str = api_config.UDISE_API_BASE_URL
API_RETRIES = api_config.API_RETRIES
LOGGER = init_logger.main(__name__)


def wait_for_next_requests_session():
    time.sleep(5)


# def check_call_status(httpResponse: requests.Response):
#     request_url = httpResponse.url
#     request_message = httpResponse.json()
#     (
#         LOGGER.info(
#             f"Request status: {request_message["status"]} for Request: {request_url}"
#         )
#         if httpResponse.status_code == 200
#         else LOGGER.info(httpResponse)
#     )


def make_get_call(target_url: str, retries=API_RETRIES):
    """
    Makes GET API call.
    """
    for connection_attempt in range(retries):
        try:
            api_session = requests.session()  # Initiate the API session
            call_response = api_session.get(url=target_url, timeout=(15))
            call_response.raise_for_status()
            # check_call_status(call_response)

            return call_response

        except requests.exceptions.ConnectTimeout:
            LOGGER.warning(
                f"Connection timeout. Retry {connection_attempt+1}/{retries}"
            )
            wait_for_next_requests_session()

        except requests.exceptions.ReadTimeout:
            LOGGER.warning(f"Read timeout. Retry {connection_attempt+1}/{retries}")
            wait_for_next_requests_session()

        except requests.exceptions.ConnectionError:
            LOGGER.warning(f"Connection error. Retry {connection_attempt+1}/{retries}")
            wait_for_next_requests_session()

        except requests.exceptions.HTTPError:
            LOGGER.warning(f"HTTP error. Retry {connection_attempt+1}/{retries}")
            wait_for_next_requests_session()

    raise Exception("API failed after retries")


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

    LOGGER.info("State ID data successfully extracted.")

    return all_state_ids


def get_district_ids(state_id_list: list) -> list:
    """
    Makes an API call for each state ID to obtain the distirct IDs.

    Return
        List of dictionaries of state-district IDs.
    """

    state_district_data = []

    state_IDs = state_id_list
    for ID in state_IDs:
        temp_district_url = str(BASE_URL + f"districts?stateId={ID}&yearId=0")
        temp_json_output = make_get_call(target_url=temp_district_url)
        temp_python_output = temp_json_output.json()

        districts_data = temp_python_output["data"]

        for district_data in districts_data:
            temp_district_id = district_data["districtId"]
            state_district_entry = {
                "stateID": ID,
                "districtID": temp_district_id,
            }  # Avoiding the need to explore the list of disctionaries later on
            state_district_data.append(state_district_entry)

    # print(state_district_data)

    LOGGER.info("All district IDs successfully extracted.")

    return state_district_data


def state_districts_urls(id_pair_list: list) -> list:
    """
    Created GET API call URLs for each state-district pair.

    Return
        List of str values for GET API calls.
    """
    all_call_urls = []

    ID_pairs = id_pair_list
    for pair_entry in ID_pairs:
        stateID = pair_entry["stateID"]
        districtID = pair_entry["districtID"]
        temp_school_data_url = str(
            BASE_URL
            + f"search-school/by-region?stateId={stateID}&districtId={districtID}"
        )
        all_call_urls.append(temp_school_data_url)

    # print(all_call_urls)

    LOGGER.info("All URLs for each state-district ID pair generated.")

    return all_call_urls


@init_logger.log_documentation_decorator
def main():
    """
    1. Define the first API GET call url
    2. Place the API GET call for state Ids
    3. Plase state-wise API GET calls for all district Ids
    4. Prepare a list of API GET call urls for each state-district pair
    """

    # STEP 1
    state_api_url_addition: str = "states?&yearId=0"
    state_api_url = str(BASE_URL + state_api_url_addition)

    # STEP 2
    state_ids = get_state_ids(state_api_url)

    # STEP 3
    ID_pair_data = get_district_ids(state_ids)

    # STEP 4
    api_call_urls = state_districts_urls(ID_pair_data)

    return api_call_urls


if __name__ == "__main__":
    main()
