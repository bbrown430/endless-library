from scaper import Scraper
from book import Book
import math

class GoodreadsScraper(Scraper):
    def __init__(self):
        super().__init__()
    
    # scrapes a list of books from a goodreads list, given the list url    
    def scrape(self, list_url):
        page = 1
    
        url_with_attrs = list_url + f"&page={page}&per_page=30" #TODO list processing
        
        soup = self.cook_soup(url_with_attrs)
        
        try:
            # determine number of books on shelf
            want_to_read_span = soup.find('span', class_='h1Shelf')
            count_text = want_to_read_span.find('span', class_='greyText').text
            want_to_read_span = soup.find('span', class_='h1Shelf')
            count_text = want_to_read_span.find('span', class_='greyText').text
            book_count = int(count_text.replace('(', '').replace(')', ''))    
            pages_needed = math.ceil(book_count / 30)
            
            goodreads_books = []
            
            print("Beginning to scrape Goodreads list.")
            while page <= pages_needed:    
                book_table = soup.find("tbody", {"id": "booksBody"})
                book_list = book_table.findAll("tr")
                for book_html in book_list:
                    goodreads_book = Book(book_html, "goodreads")
                    goodreads_books.append(goodreads_book)
                    
                page +=1
                url_with_attrs = list_url + f"&page={page}&per_page=30"
                soup = self.cook_soup(url_with_attrs)
                
            print(f"Scraping complete. {book_count} books found!")
            return goodreads_books
        except:
            return None