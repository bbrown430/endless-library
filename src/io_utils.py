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
from bs4 import BeautifulSoup

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
    def cook_soup(url):  
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
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                time.sleep(1)

            if error_count == 5:
                print("Failed to retrieve the page after 5 attempts")
                return None
    
    # downloads book from library.lol server
    def download_book(self, book):    
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        if book.genre == "non-fiction":
            cdn_url = "https://library.lol/main/"
        elif book.genre == "fiction":
            cdn_url = "https://library.lol/fiction/"
        else:
            print("Invalid genre.")
            return False
            
        url = cdn_url + book.md5
        
        dir_path = os.path.dirname(book.filepath)
        
        if not os.path.exists(dir_path): 
            os.makedirs(dir_path) 
                
        try:
            # Create an SSL context that ignores SSL certificate errors
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Make the request to the website and get the HTML content
            soup = self.cook_soup(url)
            
            if soup is not None: 
                # Find the download link in the HTML
                download_link_container = soup.find("a")
                if download_link_container is not None:
                    download_link = download_link_container["href"]
                    
                    # Make the request to the download link with SSL context
                    request = urllib.request.Request(download_link, headers=headers)
                    with urllib.request.urlopen(request, context=ssl_context) as response:
                        # Save the file
                        with open(book.filepath, "wb") as file:
                            file.write(response.read())
                        print(f".epub file downloaded successfully to: {book.filepath}")
                        return True
                else:
                    print("Download link not found.")
                    return False
            else:
                print("Download failed.")
                return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}.")
            return False
    

    # sends the book as an attachment to the kindle library
    def send_email(self, book):
        config = json.load(open("config.json"))
        email_sender = config["email_sender"]
        email_password = config["email_password"]
        email_receiver = config["email_receiver"]
        
        subject = f"Sending {book.title} to Kindle"
        
        try:  
            em = MIMEMultipart()
            em["From"] = email_sender
            em["To"] = email_receiver
            em["Subject"] = subject

            file_path = book.filepath
            attachment = open(file_path, "rb")
                            
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={book.attachment_name}")
            
            em.attach(part)
            
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, email_receiver, em.as_string())
            print(f"{book.title} successfully emailed to Kindle.")
        except smtplib.SMTPException as e:
            print(f"Error sending email: {e}.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}.")