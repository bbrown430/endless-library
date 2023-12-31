from src.scaper import Scraper
from src.book import Book
from src.io_utils import IOUtils
import validators
import math

class GoodreadsScraper(Scraper):
    def __init__(self):
        super().__init__()
    
    def link_checker(self, list_url):
        if validators.url(list_url):
            if "/review/" in list_url:
                page = 1
                formatted_url = list_url + f"&page={page}&per_page=10"
                return "profile", formatted_url
            elif "/list/show" in list_url:
                return "listopia", list_url
        else:
            False
            
    
    def how_many_books(self):
        while True:
            user_input = IOUtils.input_menu(f"This list contains {self.book_count} books. How many would you like to download?: ")
            if user_input is not None:
                try:
                    user_count = int(user_input)
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
                    continue
                if 1 <= user_count <= self.book_count:
                    self.user_count = user_count
                    return
                else:
                    print("Invalid input. Please enter a number within the valid range.")
    
    
    # scrapes a list of books from a goodreads list, given the list url    
    def scrape(self, list_url):
        page = 1
        
        type, url = self.link_checker(list_url)
        
        if not url:
            return None
        
        soup = IOUtils.cook_soup(url)
        
        try:
            goodreads_books = []
            if type == "profile":
                # determine number of books on shelf
                want_to_read_span = soup.find('span', class_='h1Shelf')
                count_text = want_to_read_span.find('span', class_='greyText').text
                want_to_read_span = soup.find('span', class_='h1Shelf')
                count_text = want_to_read_span.find('span', class_='greyText').text
                self.book_count = int(count_text.replace('(', '').replace(')', ''))    
                
                self.how_many_books()
                pages_needed = math.ceil(self.user_count / 10)
                
                while page <= pages_needed:    
                    book_table = soup.find("tbody", {"id": "booksBody"})
                    book_list = book_table.findAll("tr")
                    if page*10 > self.user_count:
                        page_amount = self.user_count % 10
                        temp_book_list = book_list[:page_amount]
                        book_list = temp_book_list
                    for book_html in book_list:
                        goodreads_book = Book(book_html, "profile")
                        goodreads_books.append(goodreads_book)
                    
                    page +=1    
                    url_with_attrs = list_url + f"&page={page}&per_page=10"
                    soup = IOUtils.cook_soup(url_with_attrs)
            
            if type == "listopia":
                book_count_container = soup.find("div", class_="stacked")
                book_string = book_count_container.text.strip().split(' books')[0].strip()
                book_count_string = book_string.replace(",", "")
                self.book_count = int(book_count_string)    
                
                self.how_many_books()
                pages_needed = math.ceil(self.user_count / 100)
                
                while page <= pages_needed:   
                    book_list = soup.find_all("tr")
                    if page*100 > self.user_count:
                        page_amount = self.user_count % 100
                        temp_book_list = book_list[:page_amount]
                        book_list = temp_book_list
                        
                    for book_html in book_list:
                        goodreads_book = Book(book_html, "listopia")
                        goodreads_books.append(goodreads_book)
                    
                    page +=1  
                    url_with_attrs = list_url + f"&page={page}"
                    soup = IOUtils.cook_soup(url_with_attrs)
            
            return goodreads_books
        except:
            return None