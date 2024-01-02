from src.anna_list import AnnaList
from src.goodreads_list import GoodreadsList
from src.searcher import Searcher
from src.io_utils import IOUtils

class Menu:
    @staticmethod
    def mission_report(failed_downloads, goodread_list_length):
        print("----------------------------------------------")
        if len(failed_downloads) > 0:
            print(f"{len(failed_downloads)}/{goodread_list_length} failed downloads:")
            for book in failed_downloads:
                print(f"\t{book.string()}")
        else:
            print("No failed downloads!")
    
    # menu flow when inputting a goodreads list
    @staticmethod
    def goodreads_menu():
        while True:
            list_input = IOUtils.input_menu("Enter a Goodreads list (type 'exit' to exit, 'back' to go back): ")
            if list_input is not None: #allow for flow back
                goodreads_list = GoodreadsList()
                goodreads_books = goodreads_list.scrape(list_url=list_input)
                if goodreads_books is not None:
                    failed_downloads = []
                    for i, goodreads_book in enumerate(goodreads_books): # loops through each book in goodreads list
                        print(f"Book {i+1}/{len(goodreads_books)} ---- {goodreads_book.string()}")
                        if not IOUtils.duplicate_checker(goodreads_book.filename):
                            search_term = f"{goodreads_book.title} {goodreads_book.author}"
                            anna_list = AnnaList()
                            anna_list = anna_list.scrape(search_term)
                            if anna_list:
                                for book in anna_list:
                                    book.update_metadata(goodreads_book, goodreads_list.list_name)
                                searcher = Searcher()
                                success = searcher.automated_search(anna_list)
                                if not success:
                                    print(f"Unable to download {goodreads_book.title} :(")
                                    failed_downloads.append(goodreads_book)
                            else:
                                print("Book not found! Skipping...")
                                failed_downloads.append(goodreads_book)
                        else:
                            print("Book already exists in downloads. Skipping...")
                            
                    Menu.mission_report(failed_downloads, len(goodreads_books))
                else:
                    print("Unable to scrpae Goodreads list! Make sure the account linked is not private.")
            if list_input is None:
                break        
    
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
    