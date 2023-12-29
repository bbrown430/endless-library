from scaper import Scraper
from book import Book

class AnnaScraper(Scraper):
    def __init__(self):
        super().__init__()
        self.base_url="https://annas-archive.org/search?index=&q="
    
    def search_formatter(self, search_term):
        formatted_search = search_term.replace(" ", "+")
        url_ending = "&ext=epub&src=lgrs&sort=&lang=en" #TODO file type and language preference     
        full_url = self.base_url + formatted_search + url_ending
        
        return full_url
    
    def list_processor(self, book_list):
        # last index grabbed is invalid
        abs_genre = book_list[0].genre
        
        # filters out unknown genres and "summary books"
        genre_filtered_list = [book for book in book_list if book.genre != "unknown" and book.genre == abs_genre]
        
        bad_terms = ["summary", "conversation starters"]
        
        term_filtered_list = [book for book in genre_filtered_list if all(bad_term not in book.title.lower() for bad_term in bad_terms)]
        
        #sorts list by filesize
        sorted_list = sorted(term_filtered_list, key=lambda book: float(book.size[:-2]))
        
        return sorted_list
    
    def scrape(self, search_term):
        url = self.search_formatter(search_term)
        while True:
            try:
                soup = self.cook_soup(url)
                books_html = soup.find_all('div', class_="h-[125] flex flex-col justify-center")
                books_html.pop()
                
                books = []
                scope = 10
                
                for book_html in books_html[:scope]:
                    book = Book(book_html, "anna")
                    books.append(book)  
                
                if books:
                    books = self.list_processor(books)
                return books
            except:
                print("Error occurred... retrying...")