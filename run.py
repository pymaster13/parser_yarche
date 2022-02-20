"""
Module allows to get all products from site 'https://yarcheplus.ru/'
and write them to .csv file
"""

from bs4 import BeautifulSoup
import csv
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import json
from logging import Logger
import os
from shutil import copyfile
import smtplib
import time
from typing import Union
import zipfile

from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains

from exceptions import (CreateLoggerFailed, OpenBrowserFailed, LoadPageFailed,
                        ChromeOptionsFailed, SpecifyAddressFailed,
                        CorrectnessStringFailed, CorrectnessNumberFailed,
                        CheckCategoriesFailed, FillCommonInfoFailed,
                        CheckingSkuImagesFailed, CheckingBagsFailed,
                        FillSkuParametersFailed, ConvertWeightVolumeFailed,
                        ParseProductFromJsonFailed, ParseProductsFromCategory,
                        GetProductsLinksFromCategory, WriteProductsToCsvFailed,
                        ParseProductsFailed, CreateZIPArchiveFailed,
                        SendZIPArchiveFailed)
from services import (create_logger, create_chrome_options, get_link,
                      initialize_browser, specify_address)
from get_categories import get_categories


# Read configuration file

with open('config.json') as config:
    config = json.load(config)

# Constants

CSV_FIELDS = ['parser_id', 'chain_id', 'tt_id', 'tt_region', 'tt_name',
              'price_datetime', 'price', 'price_promo', 'price_card',
              'price_card_promo', 'promo_start_date', 'promo_end_date',
              'promo_type', 'sku_status', 'in_stock', 'source_sku_code',
              'sku_article', 'sku_barcode', 'sku_category', 'sku_name',
              'sku_weight_min', 'sku_weight_max', 'sku_volume_min',
              'sku_volume_max', 'sku_quantity_min', 'sku_quantity_max',
              'sku_fat_min', 'sku_fat_max', 'sku_alcohol_min',
              'sku_alcohol_max', 'sku_packed', 'sku_package', 'sku_brand',
              'sku_country', 'sku_manufacturer', 'sku_parameters_json',
              'sku_link', 'app_link', 'sku_images', 'server_ip', 'dev_info',
              'promodata']

REGIONS = {'ekb': 'Екатеринбург', 'msk': 'Москва', 'spb': 'Санкт-Петербург',
           'kzn': 'Казань', 'rzn': 'Рязань', 'klg': 'Калуга',
           'rnd': 'Ростов-на-Дону', 'nsb': 'Новосибирск', 'yar': 'Ярославль',
           'nng': 'Нижний Новгород', 'krd': 'Краснодар', 'tvr': 'Тверь',
           'tms': 'Томск', 'kng': 'Калининград'}

PACKED = {'кг': 0, 'шт.': [1, 2], 'упак.': 2}

PARAMS = {'brand': 'sku_brand', 'country_of_manufacture': 'sku_country',
          'manufacturer': 'sku_manufacturer', 'weight_unit': 'sku_weight_min',
          'volume_unit': 'sku_volume_min',
          'quantity_in_package': 'sku_quantity_min', 'at_pack': 'sku_package'}


# Functions

def correct_str(string: str) -> str:
    """ Function for checking correctness string for writing to csv """

    symbols = ['&nbsp', '\n', '\r', '\t', '\xc2', '\xa0', '\\',
               '"', '”', '“', '«', '»']
    try:
        for sym in symbols:
            string = string.replace(sym, '')

        string = string.replace('  ', ' ')
        string = string.replace(';', ',')
        return string.strip()

    except Exception as e:
        raise CorrectnessStringFailed(string) from e


def correct_number(number: Union[int, float]) -> Union[int, float]:
    """ Function for checking correctness number """

    try:
        number = str(number).replace(',', '.')
        if '.' in str(number):
            whole = str(number).split('.')[0]
            fraction = str(number).split('.')[1]
            if int(fraction) == 0:
                return int(whole)

            elif 0 < int(fraction) < 100:
                while fraction:
                    if not int(fraction[-1]):
                        fraction = fraction[:-1]
                    else:
                        break

                return float(f'{whole}.{fraction}')

            elif int(fraction) > 100:
                while fraction:
                    if not int(fraction[-1]):
                        fraction = fraction[:-1]
                    else:
                        break

                if len(fraction) > 2:
                    return round(number, 2)
                else:
                    return float(f'{whole}.{fraction}')
        else:
            return int(number)

    except Exception as e:
        raise CorrectnessNumberFailed(number) from e


def check_categories(browser: Chrome, logger: Logger, cats: list = []) -> list:
    """ Function for checking categories (input cats - list of urls) """

    try:
        actual_cats = get_categories(browser)
        actual_cats_urls = [cat['url'] for _, cat in actual_cats.items()]
        if not cats:
            cats = actual_cats_urls
        else:
            low_level_cats = []
            for cat in cats:
                if cat in actual_cats_urls:
                    if '/category/' in cat:
                        low_level_cats.extend(
                                [cg['url'] for _, cg in actual_cats.items()
                                 if cg['parent_url'] == cat])

                else:
                    logger.error(f'Category "{cat}" is absent!')
            cats.extend(low_level_cats)

        # necessary to parse only low level categories
        cats = [cat for cat in cats if '/category/' not in cat]
        return cats

    except Exception as e:
        raise CheckCategoriesFailed(cats, actual_cats) from e


def fill_common_informations(result: dict, product_link: str,) -> None:
    """ Function to write common information for 1 product """

    try:
        result[product_link]['parser_id'] = config.get('parser_id', 'mc_test')
        result[product_link]['chain_id'] = config.get('chain_id', '113')
        result[product_link]['tt_region'] = REGIONS[config.get(
                                                        'tt_region', 'msk'
                                                        )]
        result[product_link]['server_ip'] = '127.0.0.1'
        result[product_link]['promodata'] = 'promodata'

    except Exception as e:
        raise FillCommonInfoFailed(product_link) from e


def check_sku_images(soup: BeautifulSoup, result: dict, link: str) -> None:
    """ Function for checking sku image flag and writing image """

    try:
        if config.get('sku_images_enable', 'true').lower() == 'true':
            if soup.find('img', class_='c1uCMShdi'):
                result[link]['sku_images'] = soup.find('img',
                                                       class_='c1uCMShdi'
                                                       )['src']
            elif soup.find('img', class_='bTBOnDBin'):
                imgs = [soup.find('img', class_='bTBOnDBin')]
                for img in soup.findAll('img', class_='b1yGNlZZL'):
                    if img not in imgs:
                        imgs.append(img)
                result[link]['sku_images'] = '|'.join([i['src'] for i in imgs])
            else:
                assert False, f'link: {link}'

    except Exception as e:
        raise CheckingSkuImagesFailed(link) from e


def check_bags(result: dict, product_link: str):
    """ Function for checking bag products and writing dev info """

    try:
        bags_links = ['/product/mayonezniy-sous-12292',
                      '/product/igrushka-myalka-antistress-26247']
        if product_link in bags_links:
            bag_info = ('Продукт расположен в категории, но '
                        'при переходе на продукт оказывается, '
                        'что он не находится ни в какой категории')
        else:
            bag_info = ''

        result[product_link]['dev_info'] = bag_info

    except Exception as e:
        raise CheckingBagsFailed(product_link) from e


def fill_sku_parameters(res: dict, link: str, product: dict) -> None:
    """ Function for checking sku_parameters flag
    and writing sku parameters of product to common dictionary """

    try:
        res[link]['sku_parameters_json'] = {}
        for prop in product['propertyValues']:
            if prop['__typename'] == 'ItemOfListPropertyValue':
                key = prop['property']['title']
                value = prop['item']['label']
                res[link]['sku_parameters_json'][key] = correct_str(value)
            elif prop['__typename'] == 'ListPropertyValue':
                key = prop['property']['title']
                value = ';'.join([part['label']
                                  for part in prop['list']])
                res[link]['sku_parameters_json'][key] = correct_str(value)
            elif prop['__typename'] == 'StringPropertyValue':
                key = prop['property']['title']
                value = prop['strValue']
                res[link]['sku_parameters_json'][key] = correct_str(value)
            else:
                assert False, 'Unknown typename'

            if config.get('sku_parameters_enable', 'true').lower() == 'true':
                for param in PARAMS:
                    if prop['property']['name'] == param:
                        if prop['__typename'] == 'ItemOfListPropertyValue':
                            res[link][PARAMS[param]] = correct_str(
                                                        prop['item']['label']
                                                        )
                        elif prop['__typename'] == 'ListPropertyValue':
                            key = prop['property']['title']
                            value = ','.join([part['label']
                                              for part in prop['list']])
                            res[link][PARAMS[param]] = correct_str(value)
                        elif prop['__typename'] == 'StringPropertyValue':
                            res[link][PARAMS[param]] = correct_str(
                                                            prop['strValue']
                                                            )
                        else:
                            assert False, 'Unknown typename'
    except Exception as e:
        raise FillSkuParametersFailed(link) from e


def convert_weight_volume(res: dict, link: str, *, param: dict) -> None:
    """ Function for checking weight and volume
    and writing this parameters of product to common dictionary """

    try:
        name = list(param.keys())[0]
        value = param[name]

        if value:
            koef = 1
            value = value.replace(',', '.')
            if 'кг' in value:
                value = value.replace('кг', '').strip()
                koef = 1000
            elif 'г' in value:
                value = value.replace('г', '').strip()
            elif 'мл' in value:
                value = value.replace('мл', '').strip()
            elif 'л' in value:
                value = value.replace('л', '').strip()
                koef = 1000
            if '-' in value:
                min_max = [float(val.strip()) for val in value.split('-')]
                res[link][f'sku_{name}_min'] = correct_number(
                                                    min_max[0] * koef
                                                    )
                res[link][f'sku_{name}_max'] = correct_number(
                                                    min_max[1] * koef
                                                    )
            else:
                if '.' in value:
                    res[link][f'sku_{name}_min'] = correct_number(
                                                    float(value) * koef
                                                    )
                else:
                    res[link][f'sku_{name}_min'] = correct_number(
                                                    int(value) * koef)
    except Exception as e:
        raise ConvertWeightVolumeFailed(link, name, value) from e


def parse_product_info_from_json(res: dict, link: str, product: dict) -> None:
    """ Function for parsing information about product from
    JSON <script> and writing info to common dictionary """

    try:
        res[link]['source_sku_code'] = product['id']
        res[link]['sku_name'] = correct_str(product['name'])

        if product['previousPrice']:
            if product['previousPrice'] > product['price']:
                res[link]['price'] = correct_number(product['previousPrice'])
                res[link]['price_promo'] = correct_number(product['price'])
        else:
            res[link]['price'] = correct_number(product['price'])

        if product['categories']:
            res[link]['sku_category'] = correct_str(
                    '|'.join([cat['name'] for cat in product['categories']]))

        fill_sku_parameters(res, link, product)

        weight = res[link].get('sku_weight_min', '')
        convert_weight_volume(res, link, param={'weight': weight})

        volume = res[link].get('sku_volume_min', '')
        convert_weight_volume(res, link, param={'volume': volume})

        packed = PACKED[product['quant']['unit']]
        if product['quant']['unit'] == 'шт.':
            if any([res[link].get('sku_volume_min', None),
                    res[link].get('sku_weight_min', None)]):
                res[link]['sku_packed'] = packed[0]
            else:
                res[link]['sku_packed'] = packed[1]
        else:
            res[link]['sku_packed'] = packed

    except Exception as e:
        raise ParseProductFromJsonFailed(link) from e


def parse_prods_links(browser: Chrome, urls: list, res: dict, tt: str) -> None:
    """ Function for parsing info about products of 1 category """

    try:
        for link in urls:
            get_link(browser, '{}{}'.format(config[('base_url')], link))

            html = browser.page_source
            soup = BeautifulSoup(html, 'lxml')

            res[link] = {}
            fill_common_informations(res, link)
            res[link]['sku_link'] = '{}{}'.format(config['base_url'], link)
            res[link]['tt_id'] = tt

            res[link]['tt_name'] = correct_str(
                        '{} ({})'.format(config.get('chain_name', 'Ярче'), tt))

            created = datetime.now()
            res[link]['price_datetime'] = created.strftime('%Y-%m-%d %H:%M:%S')

            check_sku_images(soup, res, link)

            div_sku_status = soup.find('div', class_='q1a5cSewj')
            if div_sku_status.find('div', text='Нет в наличии'):
                res[link]['sku_status'] = 0
            else:
                res[link]['sku_status'] = 1

            check_bags(res, link)

            tag = soup.find('script', charset='UTF-8')

            # delete 'window.__INITIAL_STATE__=' at the start
            # and ';' at the end
            api = json.loads(tag.string[25:-1])

            product = api['api']['product']['data']
            parse_product_info_from_json(res, link, product)

    except Exception as e:
        raise ParseProductsFromCategory(urls, link) from e


def get_products_links_from_category(browser: Chrome, url: str) -> list:
    """ Function for getting products from category HTML-page"""

    try:
        get_link(browser, url)
        try:
            show = browser.find_element_by_xpath(
                            "//span[text()='Показать ещё']")
        except Exception:
            show = None
        while show:
            ActionChains(browser).move_to_element(show).click(show).perform()
            time.sleep(2)
            try:
                show = browser.find_element_by_xpath(
                                                "//span[text()='Показать ещё']"
                                                )
            except Exception:
                break

        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')

        # In order not to take products not from the category
        rubric_all_products = soup.find('div', class_='k30d0QKVw')
        products = rubric_all_products.findAll('div', class_='c3s8K6a5X')

        if config.get('promo_only', 'false').lower() == 'true':
            promo_class = 'e10FT7BLs a3blieLf1 m3blieLf1'
            promo_products = [product for product in products
                              if product.find('div', class_=promo_class)]
            products = promo_products

        a_links_products = [prod.find('a', class_='g2mGXj5-x')
                            for prod in products]
        pure_links_products = [a['href'] for a in a_links_products]

        return pure_links_products

    except Exception as e:
        raise GetProductsLinksFromCategory(url) from e


def create_zip_archive(archive_name: str, csv_name: str) -> None:
    """ Function to create archive and add to it csv files """

    try:
        with zipfile.ZipFile(archive_name, mode='w',
                             compression=zipfile.ZIP_DEFLATED) as zf:
            zf.write(csv_name)
    except Exception as e:
        raise CreateZIPArchiveFailed(archive_name, csv_name) from e


def send_archive(name_archive: str, csv_name: str, tt_id: str) -> None:
    """ Function to send archive by mail """

    try:
        sender = config['email_from']['login']
        sender_password = config['email_from']['password']
        receivers = config['emails_to']

        smtp = smtplib.SMTP_SSL(config['email_from']['smtp'], 465)
        smtp.login(sender, sender_password)

        for receiver in receivers:
            name = config['chain_name']
            region = REGIONS[config.get('tt_region', 'msk')]
            created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            subject = f'{name} | app | {region} | {tt_id} | pd_all | {created}'
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = subject

            basename = os.path.basename(name_archive)
            with open(basename, "rb") as f:
                part = MIMEApplication(
                    f.read(),
                    Name=basename
                )
            part['Content-Disposition'] = f'attachment; filename="{basename}"'
            msg.attach(part)

            smtp.sendmail(sender, receiver, msg.as_string())

        os.remove(csv_name)
        os.remove(name_archive)

        smtp.close()

    except Exception as e:
        raise SendZIPArchiveFailed(name_archive, csv_name, tt_id) from e


def write_products_csv(dir: str, name: str, products: dict) -> None:
    """ Function to write info about products to .csv file """

    try:
        if not os.path.exists(dir):
            os.mkdir(dir)

        with open(f'{dir}/{name}', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';', )
            writer.writerow(CSV_FIELDS)

            for _, prod in products.items():
                values = [prod[f] if prod.get(f, '') else ''
                          for f in CSV_FIELDS]
                writer.writerow(values)

    except Exception as e:
        raise WriteProductsToCsvFailed(dir, name, products, prod) from e


def parse_prods(browser: Chrome, cats: list, logger: Logger, tt: str) -> str:
    """ Function for parsing information about all relevant products """

    try:
        # Confirm cookies breaks pressing on button
        try:
            cookie = browser.find_element_by_xpath(
                                "//button[@class='aJ8u8iEK8']")
            cookie.click()
        except Exception:
            cookie = None

        products = {}

        for category_url in cats:
            url = '{}{}'.format(config['base_url'], category_url)
            products_links = get_products_links_from_category(browser, url)
            if not products_links:
                logger.error(f'Неудачная попытка спарсить продукты с "{url}"')
                continue

            parse_prods_links(browser, products_links, products, tt)

        dir = config.get('output_directory', 'out')
        created = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        region = config.get('tt_region', 'msk')
        p = config.get('part_number', 'p1')

        name_csv = f'yarche_app_{region}_{tt}_{p}_pd_all_{created}.csv'
        write_products_csv(dir, name_csv, products)
        copyfile(f'{dir}/{name_csv}', name_csv)

        return name_csv

    except Exception as e:
        raise ParseProductsFailed(cats, tt) from e


def parse() -> None:
    """ Main work function launching parser """

    try:
        logger = create_logger('run.log', __name__)
        logger.debug('Parser started launched successfully.')

        options = create_chrome_options()

        logger.debug('Browser is configured successfully.')

        browser = initialize_browser(options)

        logger.debug('Browser is launched successfully.')

        tt_ids = config.get('tt_id', ["Москва, Вересаева 10"])

        for tt_id in tt_ids:
            get_link(browser, config['base_url'])

            logger.info('Page "{}" is loaded successfully.'.format(
                                                        config['base_url']))

            specify_address(browser, tt_id)

            logger.info(f'Location "{tt_id}" specifies successfully.')

            categories_from_config = config['categories'][tt_id]
            cats_for_parsing = check_categories(browser,
                                                logger,
                                                categories_from_config)

            csv_name = parse_prods(browser, cats_for_parsing, logger, tt_id)

            logger.info(f'Parsing products "{tt_id}" finished successfully.')

            name_archive = csv_name.replace('.csv', '.zip')

            create_zip_archive(name_archive, csv_name)

            send_archive(name_archive, csv_name, tt_id)

            logger.info(f'Archive "{name_archive}" with csv file is sended.')

        logger.debug('Parser finished to work.')

    except CreateLoggerFailed as e:
        print(e)
        raise

    except ChromeOptionsFailed:
        logger.exception('Creating Chrome options failed!')
        raise

    except OpenBrowserFailed:
        logger.exception('Launch of browser failed!')
        raise

    except LoadPageFailed:
        logger.exception('Loading page failed!')
        raise

    except SpecifyAddressFailed:
        logger.exception('Specify address on main page failed!')
        raise

    except CorrectnessStringFailed:
        logger.exception('Checking correctness of string failed!')
        raise

    except CorrectnessNumberFailed:
        logger.exception('Checking correctness of number failed!')
        raise

    except CheckCategoriesFailed:
        logger.exception('Checking of categories failed!')
        raise

    except FillCommonInfoFailed:
        logger.exception('Filling of common information for product failed!')
        raise

    except CheckingSkuImagesFailed:
        logger.exception('Checking and writing images for product failed!')
        raise

    except CheckingBagsFailed:
        logger.exception('Checking of bag for product failed!')
        raise

    except FillSkuParametersFailed:
        logger.exception('Filling of sku parameters for product failed!')
        raise

    except ConvertWeightVolumeFailed:
        logger.exception('Converting of weight/volume for product failed!')
        raise

    except ParseProductFromJsonFailed:
        logger.exception('Parsing JSON for product parameters failed!')
        raise

    except ParseProductsFromCategory:
        logger.exception('Parsing products from category failed!')
        raise

    except GetProductsLinksFromCategory:
        logger.exception('Parsing products links from category failed!')
        raise

    except WriteProductsToCsvFailed:
        logger.exception('Write categories to CSV-file failed!')
        raise

    except ParseProductsFailed:
        logger.exception('Parsing products failed!')
        raise

    except Exception as e:
        assert False, f'Unknown error: {e}'

    else:
        browser.quit()


if __name__ == '__main__':
    parse()
