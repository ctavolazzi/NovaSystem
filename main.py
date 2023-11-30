# NovaSystem/main.py
# Description: Entry point for the NovaSystem application.

from setup import setup_novasystem

if __name__ == '__main__':
    user_input = input("Would you like to run the setup script? (y/n): ").strip().lower()
    if user_input in ['y', 'yes']:
        setup_novasystem()
    else:
        print("Exiting program.")
        exit(0)