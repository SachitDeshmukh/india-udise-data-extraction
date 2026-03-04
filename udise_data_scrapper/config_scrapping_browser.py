# IMPORITNG CONFIG

import configuration

# IMPORTING ALL NECESSARY MODULES

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging  # Logging setup for monitoring execution

# DEFINING GLOBALS

target_website_url = configuration.UDISE_URL


# Set logging format and level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def start_driver(url: str):
    """
    Initializes and launches the automated browser session.

    Returns
    -------
    driver : selenium.webdriver.Chrome
        A Selenium browser driver used to control the webpage.
    """

    try:
        # Chrome options allow us to configure browser behaviour
        options = webdriver.ChromeOptions()

        options.add_argument(
            "--headless"
        )  # "--headless" runs the browser without opening a visible window

        # Launch the Chrome browser controlled by Selenium
        driver = webdriver.Chrome(options=options)

        # Open the UDISE Know Your School portal
        driver.get(url)

        logging.info(f"Driver successfully initiated for url: {target_website_url}")

        # Return the driver object so other functions can use it
        return driver

    except Exception as e:
        logging.error(f"Driver not initiated for url: {url} due to error: {e}")


def click_advanced_search(driver):
    """
    Waits for the "Advance Search" button to load and clicks it to display the relevant filter elements.

    Return
    -------
    None
        Button click on the webpage
    """

    try:
        wait = WebDriverWait(driver, 10)

        advance_search_button = wait.until(
            EC.presence_of_element_located((By.LINK_TEXT, "Advance Search"))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", advance_search_button
        )

        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Advance Search")))

        driver.execute_script("arguments[0].click();", advance_search_button)

        logging.info(f"Advance Search button succesffuly clicked.")

    except Exception as e:
        logging.error(f"Advance Search button was not clicked due to error: {e}")


def main():
    driver = start_driver(target_website_url)
    click_advanced_search(driver)


if __name__ == "__main__":
    main()
