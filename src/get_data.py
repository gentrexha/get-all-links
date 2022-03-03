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
import click
import pandas as pd


@click.command()
@click.option(
    "--website",
    "-w",
    help="The website from which to get all the links",
    type=click.STRING,
)
@click.option(
    "--filename",
    "-f",
    help="The output excel filename where the results should be saved. If not given defaults to website_ddmm_hhmm.xlsx",
    type=click.STRING,
    default=None,
)
def main(website, filename):
    """Gets all links from a given website and store it to given filename

    :param website: Website name from which to get links
    :param filename: Optional excel filename where to save output
    :return: Saves results into a new Excel file
    """
    logger = logging.getLogger(__name__)

    if not filename:
        filename = f"{website}_{datetime.now().strftime('%d%m_%H%M')}"

    driver = initialize_driver(website)
    result = get_data(driver=driver)
    pd.DataFrame(result).to_excel(
        data_dir / f"{filename}.xlsx", index=False
    )
    logger.info(f"Successfully saved output to {filename}.xlsx.")
    return 0


def initialize_driver(website: str):
    """Initializes chromedriver to the given website needed for further scraping.

    :param website: website to get links from
    :return: ready to scrape driver
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(f"https://{website}")
    driver.implicitly_wait(5)  # todo: find a better solution for waiting the page to load
    logging.info(f"Successfully loaded {website}.")
    return driver


def get_data(
    driver: WebDriver,
):
    """Finds all links current driver website"""
    links = driver.find_elements(By.XPATH, "//a[@href]")
    result = []
    for link in links:
        result.append({"link_text": link.text, "link_href": link.get_attribute("href")})
    logging.info(f"Found {len(links)} number of links.")
    return result


if __name__ == "__main__":
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[1]
    data_dir = project_dir / "data"

    main()
