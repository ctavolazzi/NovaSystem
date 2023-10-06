# main_app.py in the root directory

from tools.calculator.main import calculate

def main():
    result = calculate("add", 5, 3)
    print(f"Addition Result: {result}")

    result = calculate("subtract", 5, 3)
    print(f"Subtraction Result: {result}")

    result = calculate("multiply", 5, 3)
    print(f"Multiplication Result: {result}")

    result = calculate("divide", 5, 3)
    print(f"Division Result: {result}")

if __name__ == "__main__":
    main()
