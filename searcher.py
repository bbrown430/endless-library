from menu_tools import MenuTools
from io_utils import IOUtils

class Searcher:
    def automated_search(self, anna_list, metadata_source):
        if metadata_source is not None:
            abs_title = metadata_source.title
            abs_author = metadata_source.author
        
        anna_length = len(anna_list)
        # loops through all anna search results
        for i, book in enumerate(anna_list):
            if i==0:
                print(f"Downloading {abs_title} by {abs_author} ({book.size})")
            else:
                print(f"Attempting {i+1}: Downloading {abs_title} by {abs_author} ({book.size})")
            
            io_utils = IOUtils()
            successful = io_utils.download_book(book, abs_title)
            if successful:
                #send_email(book)
                print("emailing!!!")
                return True
            if i+1 == anna_length: # all sources failed
                return False

    
    def menu_formatter(self, anna_list):
        self.max_title_length = max(len(book.title) for book in anna_list)
        self.max_author_length = max(len(book.author) for book in anna_list)
        for book in anna_list:
            title_padding = ' ' * (self.max_title_length - len(book.title))
            author_padding = ' ' * (self.max_author_length - len(book.author))
            display_title = book.title + title_padding
            display_author = book.author + author_padding
            book.display_string = f"{display_title} / {display_author} / {book.size}"
    
    def interactive_search(self, anna_list):
        self.menu_formatter(anna_list)
        print(f"[#]  Title {(self.max_title_length - 5) * ' '}/ Author {(self.max_author_length - 6) * ' '}/ Size")
        for i, book in enumerate(anna_list):
            if i < 9:
                print(f"{[i+1]}  {book.display_string}")
            else:
                print(f"{[i+1]} {book.display_string}")
        while True:    
            book_number = MenuTools.input_menu("Enter the number of the book you want to select (type 'exit' to exit, 'back' to go back): ")
            if book_number is not None:
                try:
                    user_choice = int(book_number)
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
                    continue
                if 1 <= user_choice <= len(anna_list):
                    selected_book = anna_list[user_choice - 1]
                    io_utils = IOUtils()
                    successful = io_utils.download_book(selected_book, None)
                    if successful:
                        #send_email(book)
                        print("emailing!!!")
                        break
                    else:
                        print("Download failed. Try a different result.")
                else:
                    print("Invalid input. Please enter a number within the valid range.")
            if book_number is None:
                break