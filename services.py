"""
Module with functions for parsers
"""

import json
from logging import getLogger, Formatter, Logger, DEBUG, handlers
import os
import random
import time

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.keys import Keys

from exceptions import (CreateLoggerFailed, ChromeOptionsFailed,
                        OpenBrowserFailed, LoadPageFailed,
                        SpecifyAddressFailed)


# Read configuration file
with open('config.json') as config:
    config = json.load(config)


def create_logger(log_name: str, module_name) -> Logger:
    """ Function for creating and configuration of logger """

    try:
        logs_dir = config.get('logs_dir', 'logs')
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)

        logger = getLogger(module_name)
        format = '%(asctime)s %(name)s - %(levelname)s: %(message)s'
        log_formatter = Formatter(format)

        handler = handlers.RotatingFileHandler(f'{logs_dir}/{log_name}',
                                               mode='a',
                                               maxBytes=20*1024*1024,
                                               backupCount=60,
                                               encoding='utf8')
        handler.setFormatter(log_formatter)
        logger.setLevel(DEBUG)
        logger.addHandler(handler)

        return logger

    except Exception as e:
        raise CreateLoggerFailed(logs_dir, log_name) from e


def create_chrome_options() -> ChromeOptions:
    """ Function for initialization of Google Chrome browser settings """

    options = ChromeOptions()
    options.headless = True

    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')

    try:
        headers = config['headers'].get('User-Agent', '')
        options.add_argument(f'user-agent={headers}')

        return options

    except Exception as e:
        raise ChromeOptionsFailed(headers) from e


def initialize_browser(options: ChromeOptions) -> Chrome:
    """ Function to launch Google Chrome browser with created settings """

    try:
        path_to_driver = 'driver/chromedriver'
        browser = Chrome(executable_path=path_to_driver,
                         service_log_path=os.path.devnull,
                         options=options)
        return browser

    except Exception as e:
        raise OpenBrowserFailed(path_to_driver) from e


def get_link(browser: Chrome, url: str) -> bool:
    """ Function to open URL in browser Google Chrome browser """

    try:
        max_retries = config.get('max_retries', 5)
        if config['delay_range_s']:
            start_delay = config['delay_range_s'].split('-')[0]
            finish_delay = config['delay_range_s'].split('-')[1]
            delay = random.uniform(float(start_delay), float(finish_delay))
        else:
            delay = 0

        for _ in range(max_retries):
            try:
                browser.get(url)
                return
            except Exception as e:
                print(e)
                if delay:
                    time.sleep(delay)
                    delay *= config.get('backoff_factor', 1)
    except Exception as e:
        raise LoadPageFailed(url, max_retries) from e

    raise LoadPageFailed(url, max_retries)


def specify_address(browser: Chrome, address: str) -> None:
    """ Function to refine location on site 'https://yarcheplus.ru/' """

    try:
        browser.find_element_by_xpath(
                        "//button[@class='a31qlM9dd c2D0-ojBi']"
                        ).click()

        address_input = browser.find_element_by_xpath(
                        "//input[@id='receivedAddress']")
        address_input.click()
        time.sleep(1)
        address_input.clear()
        time.sleep(1)
        address_input = browser.find_element_by_xpath(
                        "//input[@id='receivedAddress']")
        address_input.click()
        address_input.send_keys(address)
        address_input.send_keys(Keys.ENTER)
        time.sleep(1)
        span = browser.find_element_by_xpath(
                        "//span[text()='Подтвердить']"
                        )
        time.sleep(1)
        span.click()
    except Exception as e:
        raise SpecifyAddressFailed(address) from e
