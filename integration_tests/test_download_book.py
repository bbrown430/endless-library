import os

from bs4 import BeautifulSoup

from src.io_utils import IOUtils
from src.book import Book

def tests_download_book():
    with open("integration_tests/feral_gods_book.html", "r") as file:
        soup = BeautifulSoup(file.read())
    book = Book(soup, "anna")
    io_utils = IOUtils()
    assert os.path.exists(book.filepath) is False
    io_utils.download_book(book)
    assert os.path.exists(book.filepath) is True
    os.remove(book.filepath)
