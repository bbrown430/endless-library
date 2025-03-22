from src.anna_list import AnnaList
from src.goodreads_list import GoodreadsList
from src.searcher import Searcher
from src.io_utils import IOUtils

class Menu:
    
    # menu flow when inputting a singular book
    @staticmethod
    def book_search_menu():
        while True:
            search_term = IOUtils.input_menu("Search for a book (type 'exit' to exit, 'back' to go back): ")
            if search_term is not None:
                anna_list = AnnaList()
                anna_list = anna_list.scrape(search_term)
                if anna_list:
                    searcher = Searcher()
                    searcher.interactive_search(anna_list)
                else:
                    print("No results! Try another search.")
            if search_term is None:
                break
    