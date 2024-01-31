import inspect
from Utils import return_input_as_string

class Debugger:
    def __init__(self, instance):
        self.name = instance.__class__.__name__
        self.instance = instance
        self.stringify = return_input_as_string

    def say(self, message):
        print(f"{self.name}: {message}")

    def return_func_name(self, func):
        # func_name = func.__name__
        return(f"{func.__name__}")