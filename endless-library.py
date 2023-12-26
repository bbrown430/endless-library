import requests
import sys
import os.path
import json
from bs4 import BeautifulSoup  
import urllib.request
from book import Book
from email.message import EmailMessage
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# returns the html of a given url
def cook_soup(url):  
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        sys.exit(f"Failed to retrieve the page. Status code: {response.status_code}")


# searches the inputted query, filtering for .epubs and libgen.li source        
def anna_search_formatter(search_term):
    base_url = "https://annas-archive.org/search?index=&q="
    formatted_search = search_term.replace(" ", "+")
    url_ending = "&ext=epub&src=lgli&sort="
    full_url = base_url + formatted_search + url_ending
    
    return full_url


def scrape_book_list(search_term):
    url = anna_search_formatter(search_term)
    soup = cook_soup(url)
    books_html = soup.find_all('div', class_="h-[125] flex flex-col justify-center")
    
    books = []
    scope = 5
    
    for book_html in books_html[:scope]:
        book = Book(book_html)
        books.append(book)
        
    return books
  
    
def select_book(book_list):
    print("Select the number of the entry you want to select:")
    for i, book in enumerate(book_list):
        print(f"{[i+1]} {book.print_metadata()}")
    
    while True:    
        try:
            user_choice = int(input("Enter the number of the book you want to select: "))
            
            # Check if the input is within the valid range
            if 1 <= user_choice <= len(book_list):
                selected_book = book_list[user_choice - 1]
                print(f"You selected: {selected_book.title}")
                return selected_book
            else:
                print("Invalid input. Please enter a number within the valid range.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    

def download_book(book):    
    cdn_urls = ["https://cdn1.booksdl.org/get.php?md5=",
                "https://cdn3.booksdl.org/get.php?md5="]

    output_file = book.title + ".epub" #TODO smartdirmake stuff =
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for cdn_url in cdn_urls:
        url = cdn_url + book.md5
        print(url)
        try:
            # Create a request with headers
            request = urllib.request.Request(url, headers=headers)

            # Open the URL and download the content
            with urllib.request.urlopen(request) as response:
                # Open a file and write the content of the response to it
                with open(output_file, "wb") as file:
                    file.write(response.read())
                print(f"EPUB file downloaded successfully to {output_file}")
                book.filepath = output_file
                return  # Break out of the loop if download is successful

        except Exception:
            print(f"CDN unavailable, attempting next CDN.")

    # If the loop completes without successful download, return an error
    print("Failed to download the book from all CDNs. Error 500.")


def send_email(book):
    config = json.load(open("config.json"))
    email_sender = config["email_sender"]
    email_password = config["email_password"]
    email_receiver = config["email_receiver"]
    
    subject = f"Sending {book.title} to Kindle"
        
    em = MIMEMultipart()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    
    # Attach a file
    file_path = book.filepath
    attachment = open(file_path, "rb")
    
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {file_path}")
    
    em.attach(part)
    
    context = ssl.create_default_context()
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    print(f"{book.title} successfully sent to Kindle.")
    

if __name__ == "__main__":
    search_term = "the lost hero"
    book_list = scrape_book_list(search_term)
    selected_book = select_book(book_list)
    download_book(selected_book)
    send_email(selected_book)