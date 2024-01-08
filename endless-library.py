import sys
from src.menu import Menu
from src.io_utils import IOUtils

if __name__ == "__main__":
    while True:
        print("===== Endless Library =====")
        print("[1] Search Mode")
        print("[2] List Mode")
        print("[3] Exit")
    
        choice = input("Enter your choice [1/2/3]: ")

        if choice == "1":
            Menu.book_search_menu()
        elif choice == "2":
            Menu.goodreads_menu()
        elif choice == "3":
            print("Exiting the program. Goodbye!")
            sys.exit("Goodbye!") 
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")