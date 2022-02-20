"""
Module with exceptions for parsers
"""

from typing import Union


# For both parsers

class ParserException(Exception):
    pass


class CreateLoggerFailed(ParserException):
    def __init__(self, dir: str, name: str) -> None:
        self.dir = dir
        self.name = name
        super().__init__(
            'Creation of logger failed!\n'
            f'Dir: {dir}\n'
            f'Logger name: {name}'
        )


class ChromeOptionsFailed(ParserException):
    def __init__(self, headers: str) -> None:
        self.headers = headers
        super().__init__(
            'Creating Chrome options failed!\n'
            f'Headers from config: {headers}'
        )


class OpenBrowserFailed(ParserException):
    def __init__(self, driver_path: str) -> None:
        self.driver_path = driver_path
        super().__init__(
            'Launch of browser failed!\n'
            f'Path to driver for browser: {driver_path}'
        )


class LoadPageFailed(ParserException):
    def __init__(self, url: str, retries: int) -> None:
        self.url = url
        self.retries = retries
        super().__init__(
            'Loading page failed!\n'
            f'Url: {url}\n'
            f'Retries: {retries}'
        )


class SpecifyAddressFailed(ParserException):
    def __init__(self, address: str) -> None:
        self.address = address
        super().__init__(
            'Specify address on main page failed!\n'
            f'Address: {address}'
        )


# For get_categories.py

class ParseCategoriesFromListFailed(ParserException):
    def __init__(self, list_categories: str) -> None:
        self.categories = list_categories
        super().__init__(
            'Parsing categories from list failed!\n'
            f'List of categories: {list_categories}'
        )


class GetCategoriesFromHtmlFailed(ParserException):
    def __init__(self) -> None:
        super().__init__('Getting categories from HTML-page failed!')


class WriteCategoriesToCsvFailed(ParserException):
    def __init__(self, dir: str, name: str, categories: dict) -> None:
        self.dir = dir
        self.name_csv = name
        self.categories = categories
        super().__init__(
            'Write categories to CSV-file failed!\n'
            f'Dir: {dir}\n'
            f'CSV-file name: {name}\n'
            f'Categories: {categories}'
        )


# For run.py

class CorrectnessStringFailed(ParserException):
    def __init__(self, string: str) -> None:
        self.string = string
        super().__init__(
            'Checking correctness of string failed!\n'
            f'String: {string}'
        )


class CorrectnessNumberFailed(ParserException):
    def __init__(self, number: Union[int, float]) -> None:
        self.string = number
        super().__init__(
            'Checking correctness of number failed!\n'
            f'Number: {number}'
        )


class CheckCategoriesFailed(ParserException):
    def __init__(self, input_cats: list, actual_cats: list) -> None:
        self.input_cats = input_cats
        self.actual_cats = actual_cats
        super().__init__(
            'Checking of categories failed!\n'
            f'Input_categories: {input_cats}\n'
            f'Actual categories: {actual_cats}'
        )


class FillCommonInfoFailed(ParserException):
    def __init__(self, product_link: str) -> None:
        self.product_link = product_link
        super().__init__(
            'Filling of common information for product failed!\n'
            f'Product link: {product_link}'
        )


class CheckingSkuImagesFailed(ParserException):
    def __init__(self, product_link: str) -> None:
        self.product_link = product_link
        super().__init__(
            'Checking and writing images for product failed!\n'
            f'Product link: {product_link}'
        )


class CheckingBagsFailed(ParserException):
    def __init__(self, product_link: str) -> None:
        self.product_link = product_link
        super().__init__(
            'Checking of bag for product failed!\n'
            f'Product link: {product_link}'
        )


class FillSkuParametersFailed(ParserException):
    def __init__(self, product_link: str) -> None:
        self.product_link = product_link
        super().__init__(
            'Filling of sku parameters for product failed!\n'
            f'Product link: {product_link}'
        )


class ConvertWeightVolumeFailed(ParserException):
    def __init__(self, link: str, name: str, value: str) -> None:
        self.link = link
        self.name = name
        self.value = value
        super().__init__(
            f'Converting of {name} for product failed!\n'
            f'Product link: {link}\n'
            f'Value of {name}: {value}'
        )


class ParseProductFromJsonFailed(ParserException):
    def __init__(self, product_link: str) -> None:
        self.product_link = product_link
        super().__init__(
            'Parsing JSON for product parameters failed!\n'
            f'Product link: {product_link}'
        )


class ParseProductsFromCategory(ParserException):
    def __init__(self, links: list, link: str) -> None:
        self.links = links
        self.link = link
        super().__init__(
            'Parsing products from category failed!\n'
            f'Products links: {links}\n'
            f'Product link: {link}'
        )


class GetProductsLinksFromCategory(ParserException):
    def __init__(self, category_link: str) -> None:
        self.category_link = category_link
        super().__init__(
            'Parsing products links from category failed!\n'
            f'Category link: {category_link}'
        )


class WriteProductsToCsvFailed(ParserException):
    def __init__(self, dir: str, name: str, prods: dict, prod: dict) -> None:
        self.dir = dir
        self.name_csv = name
        self.products = prods
        self.product = prod
        super().__init__(
            'Write categories to CSV-file failed!\n'
            f'Dir: {dir}\n'
            f'CSV-file name: {name}\n'
            f'Products: {prods}\n'
            f'Product: {prod}'
        )


class ParseProductsFailed(ParserException):
    def __init__(self, categories: list, tt: str) -> None:
        self.categories = categories
        self.tt = tt
        super().__init__(
            'Parsing products failed!\n'
            f'Categories: {categories}\n'
            f'TT: {tt}'
            )


class CreateZIPArchiveFailed(ParserException):
    def __init__(self, archive_name: str, csv_name: str) -> None:
        self.archive_name = archive_name
        self.csv_name = csv_name
        super().__init__(
            'Creating archive failed!\n'
            f'Archive: {archive_name}\n'
            f'CSV: {csv_name}'
            )


class SendZIPArchiveFailed(ParserException):
    def __init__(self, archive_name: str, csv_name: str, tt: str) -> None:
        self.archive_name = archive_name
        self.csv_name = csv_name
        self.tt = tt
        super().__init__(
            'Sending archive failed!\n'
            f'Archive: {archive_name}\n'
            f'CSV: {csv_name}\n'
            f'TT: {tt}'
            )
