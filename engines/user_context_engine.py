class UserContextEngine: 
    """
    Gathers and processes real-time user input for the Nova System
    """

def __init__(self):
    self.name = "UserContextEngine"

def gather_context(self):
    """
    Fetches user input from the command line
    """
    user_input = input("Please enter your name: ")
    return user_input

def run(self):
    """
    Runs the engine, returning or optionally logging the user data
    """
    user_data = self.gather_context()
    # Here you could store, log, or further process the user_data
    if user_data:
        print(user_data)