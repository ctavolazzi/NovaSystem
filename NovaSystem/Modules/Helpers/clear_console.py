import os
import platform

def clear_console():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

# # Use it!
# clear_console()
