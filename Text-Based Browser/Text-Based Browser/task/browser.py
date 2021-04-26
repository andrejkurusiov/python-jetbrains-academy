import argparse
import os
import re
from collections import deque
from sys import exit
from typing import Union
from urllib.parse import urlparse

import requests
from requests.exceptions import ConnectionError
import validators
from bs4 import BeautifulSoup
from colorama import Fore

INCORRECT_URL_MSG = "Incorrect URL or command!"
CONNECTION_ERROR_MSG = "Connection error occurred!"


def get_dir_name() -> str:
    """
    Reads directory name from parsed arguments
    :return: directory name
    """
    #   Parse initial argument (folder name)
    parser = argparse.ArgumentParser(
        description="This program allows our browser to store web pages in a file and show them if the user types a shortened request."
    )
    parser.add_argument("dir", help="a directory to store the files")
    args = parser.parse_args()
    return args.dir


def validate_url(url: str) -> Union[str, None]:
    """
    Validates the URL and tries with 'https://' in front if it's missing
    :param url: URL
    :return: returns valid URL or None if invalid
    """
    pattern = r"^https?:\/\/"
    # check if there's a 'http://' or 'https://' in front
    # if not, try to add missing part and then validate the URL
    if not re.match(pattern, url):
        url = "https://" + url
    return url if validators.url(url) else None


def open_url(url: str) -> Union[str, None]:
    """
    Get the text from the web-site behind given URL
    :param url: string of the url
    :return: url contents text
    """
    response = None
    with requests.Session() as session:
        # Instead of requests.get(), you'll use session.get()
        try:
            response = session.get(url)
        except ConnectionError as ce:
            print(CONNECTION_ERROR_MSG)
    return response.text if response else None
    # response.status_code == 200 else None


def filename_from_url(url: str) -> str:
    """
    Form filename from the given URL: To get the name of the file, remove the last dot and everything that comes after it.
    :param url: URL
    :return: filename (without folder)
    """
    return urlparse(url).netloc  # return domain name only


def save_file(txt: str, fname: str) -> None:
    """
    Saves given text in a given file under default directory
    :param txt: what to save
    :param fname: full filename path
    """
    with open(fname, "w", encoding="UTF-8") as file_out:
        file_out.write(txt)


def show_file(fname: str) -> None:
    """
    Print the contents of a given file
    :param fname: str
    """
    if os.access(fname, os.F_OK):
        with open(fname, "r", encoding="utf-8") as file:
            print(file.read())
            # print(line for line in file.readline())


def create_dir(directory: str) -> None:
    """
    Check and create folder for saving pages
    :param directory: new directory name
    """
    if not os.access(directory, os.F_OK):
        os.mkdir(directory)
    if not (os.access(directory, os.F_OK) and os.access(directory, os.W_OK)):
        exit(f'Error creating or accessing "{directory}" folder!')


def plain_text(html_doc: str) -> str:
    """
    Return a plain-text version of HTML document
    :param html_doc: HTML document
    :return: stripped version of text
    """
    soup = BeautifulSoup(html_doc, "html.parser")
    return soup.get_text()


def highlight_links(html_doc: str) -> str:
    """
    Return a plain-text version of HTML document with links highlighted
    :param html_doc: HTML document
    :return: stripped version of text
    """
    blue_text = Fore.BLUE  # '\033[34m'
    soup = BeautifulSoup(html_doc, "html.parser")
    links = soup.find_all("a")
    for link in links:
        link_text = str(link.text)  # str(link.string) <- not working!
        if link_text:
            link.string = "\n" + blue_text + link_text + Fore.RESET
    return soup.get_text().strip()


def browser() -> None:
    """
    Entering point
    The only argument is a folder storing the web-pages
    """
    pages_stack = deque()  # stack for web-pages
    page_cache: str = ""  # cache for saving current page

    directory: str = get_dir_name()
    create_dir(directory)

    print(
        "\n== This text-based browser returns a plain-text version of HTML document with links highlighted ==\n"
    )
    while (
        command := input('Enter an url, "back" to go back or "exit" to quit: ')
        .strip()
        .lower()
    ) != "exit":
        if command == "back":
            # Show previous page and remove it from from stack
            try:
                show_file(pages_stack.pop())
            except IndexError:
                pass
            continue

        url = validate_url(command)
        if not url:
            print(INCORRECT_URL_MSG)
            continue

        # Push previous page to stack
        if page_cache:
            pages_stack.append(page_cache)

        # Update current cache with new page (full filename path)
        page_cache = os.path.join(directory, filename_from_url(url))

        # show page from cache or display opened URL if present
        if os.access(url, os.R_OK):
            show_file(page_cache)
        else:
            page = open_url(url)
            if page:
                page = highlight_links(page)  # plain_text(page)
                print(page)
                save_file(page, page_cache)

    print("Bye!")


if __name__ == "__main__":
    browser()
