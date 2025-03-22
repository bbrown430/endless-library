import ssl
import sys
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import requests
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

from src.constants import DEBUG

class IOUtils:
    # an adaptable input menu with back and exit functionality
    @staticmethod
    def input_menu(input_message):
        while True:
            user_input = input(input_message)
            if user_input.lower() == "exit":
                sys.exit("Goodbye!")
            elif user_input.lower() == "back":
                return None
            else:
                return user_input

    @staticmethod
    def duplicate_checker(filename):
        directory = "downloads"

        all_files = []

        # Walk through all directories and subdirectories
        for path, subdirs, files in os.walk(directory):
            for name in files:
                all_files.append(name)

        if filename in all_files:
            return True
        else:
            return False

    # returns HTML from a website into a parseable format
    @staticmethod
    def cook_soup(url, cdn=None):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        error_count = 0
        while True:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup
            elif response.status_code == 500:
                error_count += 1
                print("Internal Server Error! Retrying in 2 seconds...")
                time.sleep(2)
            elif response.status_code == 429:
                error_count += 1
                print("Moving too fast! Retrying in 10 seconds...")
                time.sleep(10)
            else:
                error_count += 1
                # if DEBUG:
                #     print(f"url={url}")
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                time.sleep(1)

            if error_count == 5:
                print("Failed to retrieve the page after 5 attempts")
                return None

    @staticmethod
    def get_cdn():
        cdn = LimitedRotatingBookCDN(
            ["https://libgen.is", "https://libgen.rs", "https://libgen.st"]
        )
        return cdn

    # downloads book from library.lol server
    def download_book(self, book, cdn=None):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        if cdn is None:
            cdn = IOUtils().get_cdn()
        dir_path = os.path.dirname(book.filepath)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        libgenrs_soup = None
        while True:
            book_url = cdn.get_book_url(book)
            print(f"Attempting to download {book.title} from {cdn.cur_url}...")
            try:
                libgenrs_soup = self.cook_soup(book_url)
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {book.title} from {cdn.cur_url} due to: {e}.")
                try:
                    cdn.next()
                except StopIteration:
                    break
                continue
            if libgenrs_soup is None:
                try:
                    cdn.next()
                except StopIteration:
                    break
                continue
            break
        if libgenrs_soup is not None:
            try: 
                download_link_container = libgenrs_soup.find("a", string=("Libgen.rs", "Libgen & IPFS & Tor"))
                if download_link_container:
                    booksms_downloadlink = download_link_container.get("href")
                    booksms_soup = self.cook_soup(booksms_downloadlink)
                    abs_download_link_container = booksms_soup.find("a", string="GET")
                    if abs_download_link_container:
                        abs_download_link = abs_download_link_container.get("href")
                    
                    print(abs_download_link)

                request = urllib.request.Request(abs_download_link, headers=headers)
                print(f"Downloading {book.title} from {abs_download_link}...")
                with urllib.request.urlopen(request) as response:
                    with open(book.filepath, "wb") as file:
                        file.write(response.read())
                    print(f".epub file downloaded successfully to: {book.filepath}")
                    return True
            except Exception as e:
                print(f"An unexpected error occurred: {e}.")
                return False
        else:
            print(f"Download failed.")
            return False


    # sends the book as an attachment to the kindle library
    def send_email(self, book, user: str):
        try:
            # Load config and user email mappings
            config = json.load(open("config.json"))
            users = json.load(open("users.json"))

            email_sender = config["email_sender"]
            email_password = config["email_password"]

            # Look up the receiver email from users.json
            email_receiver = users.get(user.lower())
            if not email_receiver:
                print(f"User '{user}' not found in users.json.")
                return False

            subject = f"Sending {book.title} to Kindle"

            # Build email
            em = MIMEMultipart()
            em["From"] = email_sender
            em["To"] = email_receiver
            em["Subject"] = subject

            # Attach file
            with open(book.filepath, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={book.attachment_name}")
                em.attach(part)

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())

            print(f"{book.title} successfully emailed to {email_receiver}.")
            return True

        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}.")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}.")
            return False

class LimitedRotatingBookCDN:
    """A rotating CDN for downloading books from multiple sources"""
    def __init__(self, urls):
        if isinstance(urls, str):
            urls = [urls]
        self.urls = urls
        self.url_index = 0
        self.cur_url = self.urls[self.url_index]

    def next(self):
        self.url_index += 1
        if self.url_index >= len(self.urls):
            raise StopIteration
        else:
            self.cur_url = self.urls[self.url_index]
        return self.cur_url

    def get_url(self, suffix=None):
        if suffix is None:
            return self.cur_url
        return f"{self.cur_url}/{suffix}"

    def __len__(self):
        return len(self.urls)

    def get_book_url(self, book):
        if DEBUG:
            print("Book genre:", book.genre)
        if book.genre == "non-fiction":
            url = self.get_url(f"book/index.php?md5={book.md5}")
        elif book.genre == "fiction":
            cdn_url = self.get_url("fiction")
            if not cdn_url.endswith("/"):
                cdn_url += "/"
            url = cdn_url + book.md5
        else:
            url = self.get_url()

        if DEBUG:
            print(f"get_book_url url: {url}")
        return url


def get_ipfs_link(soup):
    for anchor in soup.find_all('a'):
        if "IPFS" in anchor.text or "IPFS" in anchor['href']:
            ipfs_link = anchor['href']
            return ipfs_link
