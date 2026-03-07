# IMPORITNG INTERNAL MODULES

import configuration
import config_scrapping_browser

# IMPORTING ALL NECESSARY MODULES

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import logging

# DEFINING GLOBALS

source_url = configuration.UDISE_URL
webDriver = config_scrapping_browser.main()

# Set logging format and level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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

        # Allow webpage time to load initial dropdowns
        time.sleep(3)

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

        # Allow webpage time to load initial dropdowns
        time.sleep(3)

        try:
            for state in list_of_states:
                self.state_dropdown.select_by_visible_text(state)

                # Wait for district dropdown to populate
                time.sleep(2)

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
            logging.error(f"Unable to extract district data for state: {state}.")

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


def main():
    Scraper = Navigator(webDriver)
    all_districts = Scraper.scrape_district_list()

    return all_districts


if __name__ == "__main__":
    main()
