import webbrowser
import os

# Assuming hero.html is in the same directory as this script
file_path = 'file://' + os.path.realpath('hero.html')
webbrowser.open(file_path)