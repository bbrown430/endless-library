from email.message import EmailMessage
import ssl
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import requests
import urllib.request
from bs4 import BeautifulSoup

class IOUtils:
    def cook_soup(self, url):  
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
                error_count +=1
                print("for me")
                time.sleep(2)
            elif response.status_code == 429:
                error_count +=1
                print("Moving too fast! Retrying in 10 seconds...")
                time.sleep(10)
            else:
                error_count +=1
                print(f"Failed to retrieve the page. Status code: {response.status_code}")
                time.sleep(1)
                
            if error_count == 5:
                break   
    
    # downloads book from library.lol server
    def download_book(self, book, abs_title):    
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
            
        if book.genre == "non-fiction":
            cdn_url = "https://library.lol/main/"
        if book.genre == "fiction":
            cdn_url = "https://library.lol/fiction/"
            
        url = cdn_url + book.md5
        
        if not os.path.exists("downloads"): 
            os.makedirs("downloads") 
            
        if abs_title is None:
            title = book.title
        else:
            title = abs_title
        
        output_file = "downloads/" + title + ".epub" #TODO redeclaration
        
        soup = self.cook_soup(url)
        if soup is not None: 
            download_link = soup.find("a")["href"] 
            try:
                request = urllib.request.Request(download_link, headers=headers)
                with urllib.request.urlopen(request) as response:
                    with open(output_file, "wb") as file:
                        file.write(response.read())
                    print(f".epub file downloaded successfully to {output_file}")
                    book.filepath = output_file
                    return True

            except Exception as e:
                print(f"Download failed here due to: {e}.")
                return False
        else:
            print(f"Download failed.")
            return False
    
    # sends the book as an attachment to the kindle library
    def send_email(self, book, abs_title):
        config = json.load(open("config.json"))
        email_sender = config["email_sender"]
        email_password = config["email_password"]
        email_receiver = config["email_receiver"]
        
        subject = f"Sending {book.title} to Kindle"
            
        em = MIMEMultipart()
        em["From"] = email_sender
        em["To"] = email_receiver
        em["Subject"] = subject
        
        if abs_title is None: #TODO bad practice
            title = book.title
        else:
            title = abs_title
        
        # Attach a file
        file_path = book.filepath
        attachment = open(file_path, "rb")
        
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        filename = title + ".epub"
        part.add_header("Content-Disposition", f"attachment; filename={filename}")
        
        em.attach(part)
        
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())
        print(f"{title} successfully sent to Kindle.")