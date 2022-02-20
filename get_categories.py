"""
Module allows to get all categories from site 'https://yarcheplus.ru/'
and write them to .csv file
"""

from bs4 import BeautifulSoup
import csv
from datetime import datetime
import json
import os

from selenium.webdriver import Chrome

from exceptions import (CreateLoggerFailed, ParseCategoriesFromListFailed,
                        OpenBrowserFailed, LoadPageFailed, ChromeOptionsFailed,
                        SpecifyAddressFailed, GetCategoriesFromHtmlFailed,
                        WriteCategoriesToCsvFailed)
from services import (create_logger, create_chrome_options, get_link,
                      initialize_browser, specify_address)


# Read configuration file

with open('config.json') as config:
    config = json.load(config)


# Functions

def parse_categories_from_list(cats: list, result: dict = {}) -> dict:
    """ Function for extracting categories from an already preprocessed
    list """

    try:
        for cat in cats:
            # if both == False - category is not showed on page
            if any((cat['isCatalogDisplay'], cat['isCategoryDisplay'])):
                id = cat['treeId']
                result[id] = {}
                result[id]['parent_id'] = cat['parentTreeId']

                if cat['isCatalogDisplay']:
                    result[id]['url'] = '/catalog/{}-{}'.format(cat['code'],
                                                                cat['id'])
                else:
                    result[id]['url'] = '/category/{}-{}'.format(cat['code'],
                                                                 cat['id'])
                if cat['parentTreeId']:
                    result[id]['name'] = '{}|{}'.format(
                                        result[cat['parentTreeId']]['name'],
                                        cat['name'])
                    result[id]['parent_url'] = result[
                                                cat['parentTreeId']
                                                ]['url']
                else:
                    result[id]['name'] = cat['name']
                    result[id]['parent_url'] = ''

                if cat['children']:
                    parse_categories_from_list(cat['children'], result)

        return result

    except Exception as e:
        raise ParseCategoriesFromListFailed(cats) from e


def get_categories(browser: Chrome) -> dict:
    """ Function for getting categories from HTML-page """

    try:
        url = '{}/category/'.format(config['base_url'])
        get_link(browser, url)

        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')

        # get <script> with categoryList
        tag = soup.find('script', charset='UTF-8')

        # delete 'window.__INITIAL_STATE__=' at the start
        # and ';' at the end
        api = json.loads(tag.string[25:-1])

        categories = parse_categories_from_list(
                        api['api']['categoryList']['list'])

        return categories

    except Exception as e:
        raise GetCategoriesFromHtmlFailed from e


def write_categories_to_csv(dir: str, name: str, categories: dict) -> None:
    """ Function to write categories to .csv file """

    try:
        if not os.path.exists(dir):
            os.mkdir(dir)

        with open(f'{dir}/{name}', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['id', 'parent_id', 'name', 'url', 'parent_url'])

            for id, fields in categories.items():

                writer.writerow([id, fields['parent_id'], fields['name'],
                                fields['url'], fields['parent_url']])
    except Exception as e:
        raise WriteCategoriesToCsvFailed(dir, name, categories) from e


def parse() -> None:
    """ Main work function launching parser """

    try:
        logger = create_logger('get_categories.log', __name__)
        logger.debug('Parser started successfully.')

        options = create_chrome_options()

        logger.debug('Browser is configured successfully.')

        browser = initialize_browser(options)

        logger.debug('Browser is launched successfully.')

        tt_ids = config.get('tt_id', ["Москва, Вересаева 10"])

        for tt_id in tt_ids:
            get_link(browser, config['base_url'])

            logger.info('Page "{}" is loaded successfully.'.format(
                                                        config['base_url'])
                        )

            specify_address(browser, tt_id)

            logger.info(f'Location "{tt_id}" is specified successfully.')

            categories = get_categories(browser)

            logger.info("Categories are parsed from HTML-page successfully.")

            dir = config.get('output_directory', 'out')
            datetime_creation = datetime.now()
            datetime_creation = datetime_creation.strftime(
                                            '%Y-%m-%d %H:%M:%S'
                                            )
            name_csv = f'categories ({tt_id}) - {datetime_creation}.csv'
            write_categories_to_csv(dir, name_csv, categories)

            logger.info(f'All parsed categories are writed to "{name_csv}".')
            logger.debug('Parser finished to work.')

    except CreateLoggerFailed:
        logger.exception('Creation of logger failed!')
        raise

    except ChromeOptionsFailed:
        logger.exception('Creating Chrome options failed!')
        raise

    except OpenBrowserFailed:
        logger.exception('Launch of browser failed!')
        raise

    except LoadPageFailed:
        logger.exception('Page loading is failed!')
        raise

    except SpecifyAddressFailed:
        logger.exception('Specify address on main page failed!')
        raise

    except ParseCategoriesFromListFailed:
        logger.exception('Parsing categories from list failed!')
        raise

    except GetCategoriesFromHtmlFailed:
        logger.exception('Getting categories from HTML-page failed!')
        raise

    except WriteCategoriesToCsvFailed:
        logger.exception('Write categories to CSV-file failed!')
        raise

    except Exception as e:
        assert False, f'Unknown error: {e}'

    else:
        browser.quit()


if __name__ == '__main__':
    parse()
