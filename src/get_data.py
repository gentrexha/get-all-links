#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import click
import pandas as pd
from tqdm import tqdm


@click.command()
@click.option(
    "--filename",
    "-f",
    help="The output excel filename where the results should be saved. If not given defaults to website_ddmm_hhmm.xlsx",
    type=click.STRING,
    default=None,
)
def main(filename):
    """Gets all links from a given website and store it to given filename

    :param filename: Optional excel filename where to save output
    :return: Saves results into a new Excel file
    """
    logger = logging.getLogger(__name__)

    if not filename:
        filename = f"bbc_{datetime.now().strftime('%d%m_%H%M')}"

    driver = initialize_driver()
    result = get_data(driver=driver)
    pd.DataFrame(result).to_excel(DATA_DIR / f"{filename}.xlsx", index=False)
    logger.info(f"Successfully saved output to {filename}.xlsx")
    return 0


def initialize_driver(website: str = "www.bbc.com"):
    """Initializes chromedriver to the given website needed for further scraping.

    :param website: website to get links from
    :return: ready to scrape driver
    """
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"https://{website}")
    # wait for page to load
    driver.implicitly_wait(DELAY)
    logging.info(f"Successfully loaded {website}")
    return driver


def get_data(driver: WebDriver):
    """Finds all links current driver website"""
    results = []
    stored_links = []

    logging.info("Getting all links from homepage")
    links = driver.find_elements(By.XPATH, "//a[@href]")
    for link in tqdm(links):
        stored_links.append(
            {"link.text": link.text, "link.href": link.get_attribute("href")}
        )

    logging.info("Getting title and description from all stored links")
    for link in tqdm(stored_links):
        try:
            driver.get(link["link.href"])
            # wait for page to load
            element_present = EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1[class*='qa-story-headline']")
            )
            WebDriverWait(driver, DELAY).until(element_present)
            # get data
            title = driver.find_element(
                By.CSS_SELECTOR, "h1[class*='qa-story-headline']"
            ).text
            description = driver.find_element(
                By.CSS_SELECTOR, "div[class*='qa-story-body']"
            ).text

        except (NoSuchElementException, TimeoutException):
            title = "na"
            description = "na"
            logging.error(
                f"Could not find title and description from link={link['link.href']}"
            )

        results.append(
            {
                "link_text": link["link.text"],
                "link_href": link["link.href"],
                "title": title,
                "description": description,
            }
        )

    logging.info(f"Found {len(links)} number of links")
    return results


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    PROJECT_DIR = Path(__file__).resolve().parents[1]
    DATA_DIR = PROJECT_DIR / "data"
    # amount of seconds to wait for pages to load
    DELAY = 5

    main()
