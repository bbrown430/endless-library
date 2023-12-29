import sys

class MenuTools:
    @staticmethod
    def input_menu(input_message):
        while True:
            user_input = input(input_message)
            if user_input.lower() == "exit":
                sys.exit("Goodbye!")
            elif user_input.lower() == "back":
                return None
            else:
                return user_input
            
    