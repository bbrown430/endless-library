import requests
import sys
import math
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
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

# searches the inputted query, filtering for .epubs and libgen.li source        
def anna_search_formatter(search_term):
    base_url = "https://annas-archive.org/search?index=&q="
    formatted_search = search_term.replace(" ", "+")
    url_ending = "&ext=epub&src=lgrs&sort=&lang=en"
    full_url = base_url + formatted_search + url_ending
    
    return full_url

# formats goodreads list from your profile url
def goodreads_scraper(list_url):
    page = 1
    
    #list_url = "https://www.goodreads.com/review/list/140481239?shelf=to-read"
    url_with_attrs = list_url + f"&page={page}&per_page=30"
    
    soup = cook_soup(url_with_attrs)
    
    # determine number of books on shelf
    want_to_read_span = soup.find('span', class_='h1Shelf')
    count_text = want_to_read_span.find('span', class_='greyText').text
    want_to_read_span = soup.find('span', class_='h1Shelf')
    count_text = want_to_read_span.find('span', class_='greyText').text
    book_count = int(count_text.replace('(', '').replace(')', ''))    
    pages_needed = math.ceil(book_count / 30)
    
    book_strings = []
    while page <= pages_needed:    
        book_table = soup.find("tbody", {"id": "booksBody"})
        book_list = book_table.findAll("tr")
        for book_html in book_list:
            title = book_html.select_one('td.field.title a[title]').text.strip()
            if "\n" in title:
                split_title = title.split("\n")
                title = split_title[0]
            author = book_html.select_one('td.field.author a[href]').text
            
            book_strings.append(title + " " + author)
            
        page +=1
        url_with_attrs = list_url + f"&page={page}&per_page=30"
        soup = cook_soup(url_with_attrs)
    
    return book_strings
        
# scrapes the first 10 (or less) books from Anna's Archive
def scrape_book_list(search_term):
    url = anna_search_formatter(search_term)
    soup = cook_soup(url)
    books_html = soup.find_all('div', class_="h-[125] flex flex-col justify-center")
    
    books = []
    scope = 10
    
    for book_html in books_html[:scope]:
        book = Book(book_html)
        books.append(book)
        
    return books
  
# allows user to select book form list of scraped entries    
def select_book_menu(book_list):
    max_title_length = max(len(book.title) for book in book_list)
    max_author_length = max(len(book.author) for book in book_list)
    for book in book_list:
        title_padding = ' ' * (max_title_length - len(book.title))
        author_padding = ' ' * (max_author_length - len(book.author))
        book.display_title = book.title + title_padding
        book.display_author = book.author + author_padding
    
    print("Select the number of the book you want to select: ")
    print(f"[#]  Title {(max_title_length - 5) * ' '}/ Author {(max_author_length - 6) * ' '}/ Size")
    for i, book in enumerate(book_list):
        if i < 9:
            print(f"{[i+1]}  {book.print_metadata()}")
        else:
            print(f"{[i+1]} {book.print_metadata()}")
    
    while True:    
        try:
            user_input = input("Enter the number of the book you want to select (type 'exit' to exit, 'back' to go back): ")
            
            if user_input.lower() == 'exit':
                sys.exit("Goodbye!")

            elif user_input.lower() == 'back':
                break

            else:
                user_choice = int(user_input)
                
                if 1 <= user_choice <= len(book_list):
                    selected_book = book_list[user_choice - 1]
                    print(f"You selected: {selected_book.title}")
                    return(selected_book)
                else:
                    print("Invalid input. Please enter a number within the valid range.")

        except ValueError:
            print("Invalid input. Please enter a numeric value.")
    
# downloads book from library.lol server
def download_book(book):    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    cdn_url = "https://library.lol/fiction/"
    url = cdn_url + book.md5

    output_file = book.title + ".epub" #TODO smartdirmake stuff =
    
    soup = cook_soup(url)
    if soup is not None:
        download_link = soup.find("a")["href"]
        pruned_link = download_link.split(".epub")[0]
        real_link = pruned_link + ".epub/"        
        try:
            request = urllib.request.Request(real_link, headers=headers)

            with urllib.request.urlopen(request) as response:
                with open(output_file, "wb") as file:
                    file.write(response.read())
                print(f"EPUB file downloaded successfully to {output_file}")
                book.filepath = output_file
                return 

        except Exception as e:
            print(f"Download failed here due to: {e}.")
            return
    else:
        print(f"Download failed there.")
        return
        
# sends the book as an attachment to the kindle library
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
    
# allows user to input a book and search for it
def book_search_menu():
    while True:
        search_term = input("Search for a book (type 'exit' to exit, 'back' to go back): ")
        if search_term.lower() == "exit":
            sys.exit("Goodbye!")
        elif search_term.lower() == "back":
            break
        else:
            book_list = scrape_book_list(search_term)
            selected_book = select_book_menu(book_list)
            if selected_book is not None:
                download_book(selected_book)
                if selected_book.filepath is not None:
                    send_email(selected_book)

def goodreads_menu():
    while True:
        list_input = input("Enter a Goodreads list (type 'exit' to exit, 'back' to go back): ")
        if list_input.lower() == "exit":
            sys.exit("Goodbye!")
        elif list_input.lower() == "back":
            break
        else:
            book_searches = goodreads_scraper(list_input)
            
            for book_string in book_searches:
                book_list = scrape_book_list(book_string)
                selected_book = book_list[0]
                print(f"Downloading {selected_book.title} by {selected_book.author}")
                if selected_book is not None:
                    download_book(selected_book)
                    if selected_book.filepath is not None:
                        #send_email(selected_book)
                        print("emailing!!!")

# main menu flow
def main_menu():
    while True:
        print("===== Endless Library =====")
        print("[1] Search Mode")
        print("[2] Import from Goodreads list")
        print("[3] Exit")
    
        choice = input("Enter your choice [1/2/3]: ")

        if choice == "1":
            book_search_menu()
        elif choice == "2":
            goodreads_menu()
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            sys.exit("Goodbye!") 
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main_menu()