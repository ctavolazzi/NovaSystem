# main.py inside the calculator folder

def calculate(operation, x, y):
    if operation == "add":
        return x + y
    elif operation == "subtract":
        return x - y
    elif operation == "multiply":
        return x * y
    elif operation == "divide":
        return x / y if y != 0 else "Cannot divide by zero"
    else:
        return "Invalid operation"
