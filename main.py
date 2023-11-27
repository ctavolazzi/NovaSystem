import os
import sys
import time
import argparse
from src.utils.stream_to_console import stream_to_console as stc
from src.utils.generate_file_structure import generate_file_structure
from src.tests.test_stc import test_stc

# Set up global variables
# (Add any necessary global variables here)
tests = [test_stc]

def run_tests(tests):
    results = []
    for test in tests:
        result = test()
        results.append(result)
    return results

def main():
    # Get the root directory where the script is being run
    root_directory = os.path.dirname(os.path.abspath(__file__))

    # Print the root directory
    print(f"Root directory: {root_directory}")

    parser = argparse.ArgumentParser(description='NovaSystem Main Script')
    parser.add_argument('--test', action='store_true', help='Run tests')
    args = parser.parse_args()

    # Welcome message
    stc("Hello, I am NovaSystem AI.")

    if args.test:
        test_results = run_tests(tests)
        for result in test_results:
            print(result)
    else:
        # Standard operation
        print("Standard system message.")

        output_directory = os.path.join(root_directory, 'output')
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        output_filename = f'NovaSystem_file_structure_{time.time()}.txt'
        generate_file_structure(root_directory, os.path.join(output_directory, output_filename))

        # Additional functionalities
        # (Add more code here as needed)

if __name__ == "__main__":
    main()
