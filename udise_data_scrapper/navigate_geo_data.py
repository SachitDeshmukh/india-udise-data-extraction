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


def get_dropdown_options(select_element):
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
            f"Found {len(valid_options)} options for WebElement: {select_element} on website: {source_url}"
        )

        return valid_options

    except Exception as e:
        logging.error(
            f"Options not found for WebElement: {select_element} on website: {source_url}"
        )


def scrape_state_list():
    """
    Scrapes the list of all states and union teritories on the "State" dropdown.

    Returns
    -------
    list of str values
    """

    driver = webDriver

    # Allow webpage time to load initial dropdowns
    time.sleep(3)

    try:
        state_dropdown = Select(
            driver.find_element(
                By.XPATH, "//label[normalize-space()='State']/following::select[1]"
            )
        )

    except Exception as e:
        logging.error(f"Unable to locate data by provided element type.")

    state_list = get_dropdown_options(state_dropdown._el)

    return state_dropdown, state_list


def main():
    scrape_state_list()


if __name__ == "__main__":
    main()
