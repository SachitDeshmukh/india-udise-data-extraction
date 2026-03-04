# IMPORITNG CONFIG

import configuration

# IMPORTING ALL NECESSARY MODULES

from selenium import webdriver
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


def main():
    start_driver(target_website_url)


if __name__ == "__main__":
    main()
