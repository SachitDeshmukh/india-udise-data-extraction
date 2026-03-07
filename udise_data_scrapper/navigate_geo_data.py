# IMPORITNG INTERNAL MODULES

import configuration
import config_scrapping_browser

# IMPORTING ALL NECESSARY MODULES

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import logging
import pandas as pd
from joblib import Parallel, delayed  # Parallel execution for simulations

# DEFINING GLOBALS

source_url = configuration.UDISE_URL

# Set logging format and level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def let_options_load():
    # Allow webpage time to load data of dropdowns
    time.sleep(1)


def get_dropdown_options(select_element, element_description: str):
    """
    Extracts all selectable values from a dropdown menu.

    Parameters
    ----------
    select_element : selenium WebElement
        The HTML <select> element representing a dropdown menu.

    Returns
    -------
    list
        A list of visible option names in the dropdown.
    """
    try:
        # Find all <option> tags inside the dropdown
        options = select_element.find_elements(By.TAG_NAME, "option")

        # Extract visible text from each option
        # Exclude placeholder entries like "Select"

        valid_options = [o.text for o in options if o.text.strip() != "Select"]
        logging.info(
            f"Found {len(valid_options)} options for elememt: {element_description} on website: {source_url}"
        )

        return valid_options

    except Exception as e:
        logging.error(
            f"Options not found for current WebElement on website: {source_url} due to error: {e}"
        )


class Navigator:
    """
    A class for scraping state and district dropdown data from a webpage.

    Attributes
    ----------
    driver : webdriver
        The Selenium WebDriver instance used for scraping.
    """

    def __init__(self, web_driver):
        """
        Parameters
        ----------
        web_driver : webdriver
            The Selenium WebDriver instance to use for scraping.
        """
        self.driver = web_driver

    def scrape_state_list(self):
        """
        Scrapes the list of all states and union territories on the "State" dropdown.

        Returns
        -------
        tuple : (Select, list of str)
            The state dropdown element and a list of state names.
        """

        let_options_load()

        try:
            state_dropdown = Select(
                self.driver.find_element(
                    By.XPATH, "//label[normalize-space()='State']/following::select[1]"
                )
            )

            self.state_dropdown = state_dropdown  # Allowing to use this across the code

        except Exception as e:
            logging.error(
                f"Unable to locate data by provided element type due to error: {e}."
            )

        state_list = get_dropdown_options(state_dropdown._el, "States")

        return state_list

    def search_district_dropdown(self):
        try:
            district_dropdown = Select(
                self.driver.find_element(
                    By.XPATH,
                    "//label[normalize-space()='District']/following::select[1]",
                )
            )

            return district_dropdown

        except Exception as e:
            logging.error(
                f"Unable to locate data by provided element type due to error: {e}."
            )

    def scrape_district_list(self):
        """
        Scrapes the list of districts for each state on the "District" dropdown.

        Returns
        -------
        list of dict
            A list of dicts, each containing a 'State' key and a 'Districts' key.
        """

        all_districts_list: list = []

        list_of_states = self.scrape_state_list()

        let_options_load()

        try:
            for state in list_of_states:
                self.state_dropdown.select_by_visible_text(state)

                let_options_load()

                district_dropdown = self.search_district_dropdown()

                districts_temp = get_dropdown_options(
                    district_dropdown._el, f"Districts for state: {state}"
                )

                all_districts_list.append(
                    {
                        "State": state,
                        "Districts": districts_temp,
                    }
                )

        except Exception as e:
            logging.error(
                f"Unable to extract district data for state: {state} due to error: {e}."
            )

        return all_districts_list

    def search_block_dropdown(self):
        try:
            block_dropdown = Select(
                self.driver.find_element(
                    By.XPATH,
                    "//label[normalize-space()='Block']/following::select[1]",
                )
            )

            return block_dropdown

        except Exception as e:
            logging.error(
                f"Unable to locate data by provided element type due to error: {e}."
            )

    def prep_block_scrapping(self):
        """
        Scrapes the list of block for each state-district pair on the "Block" dropdown.

        Returns
        -------
        list of dict
            A list of dicts, each containing a 'State' key, 'District' key, and 'Blocks' key.
        """
        state_district_list = self.scrape_district_list()

        state_district_dataframe = pd.DataFrame(state_district_list).explode(
            "Districts"
        )

        # Converts the list of distictionaries into a pandas DataFrame with
        # column 1 for "State" values and column 2 for all "District" values

        state_district_pairs = state_district_dataframe.to_dict(
            orient="records"
        )  # Outputs a list of dictionary with each key-value pair of state-district

        district_chunks = configuration.DISTRICT_CHUNKS

        for i in range(0, len(state_district_pairs), district_chunks):
            yield state_district_pairs[i : i + district_chunks]


def parallel_scraping_block_list(districts_batch):

    driver = config_scrapping_browser.main()  # create new headless driver

    all_block_list = []

    try:
        for state_district_pair in districts_batch:

            state = state_district_pair["State"]
            district = state_district_pair["Districts"]

            let_options_load()

            state_dropdown = Select(
                driver.find_element(
                    By.XPATH,
                    "//label[normalize-space()='State']/following::select[1]",
                )
            )

            state_dropdown.select_by_visible_text(state)

            let_options_load()

            district_dropdown = Select(
                driver.find_element(
                    By.XPATH,
                    "//label[normalize-space()='District']/following::select[1]",
                )
            )

            district_dropdown.select_by_visible_text(district)

            let_options_load()

            block_dropdown = Select(
                driver.find_element(
                    By.XPATH,
                    "//label[normalize-space()='Block']/following::select[1]",
                )
            )

            blocks = get_dropdown_options(
                block_dropdown._el,
                f"Blocks for district: {district} in state: {state}",
            )

            all_block_list.append(
                {"State": state, "District": district, "Blocks": blocks}
            )

        return all_block_list

    finally:
        driver.quit()


def initializing_scraping():
    webDriver = config_scrapping_browser.main()
    Scraper = Navigator(webDriver)
    STATE_DISTRICT_PAIR_BATCHES = list(Scraper.prep_block_scrapping())
    Scraper.driver.quit()  # Close the headless broswer after obtaining frist level data

    all_blocks_data = Parallel(n_jobs=configuration.PARALLEL_JOBS, backend="loky")(
        delayed(parallel_scraping_block_list)(districts_batch)
        for districts_batch in STATE_DISTRICT_PAIR_BATCHES
    )

    return all_blocks_data


def main():
    initializing_scraping()


if __name__ == "__main__":
    main()
