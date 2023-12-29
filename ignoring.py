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
            while True:
                selected_book = select_book_menu(book_list)
                if selected_book is not None:
                    download_book(selected_book, None)
                    if selected_book.filepath is not None:
                        print("emailing...")
                        break
                        #send_email(selected_book, None)
                    else:
                        print("Download failed. Try a different book.")
                else:
                    break
            
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