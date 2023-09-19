import ast

def analyze_python_code_skip_malformed(file_path):
    with open(file_path, 'r') as f:
        code = f.read().split('\n')

    # Initialize dictionaries to store unique functions and classes
    unique_functions = {}
    unique_classes = {}

    # Try to parse each line of code; skip malformed chunks
    for line in code:
        try:
            tree = ast.parse(line)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    unique_functions[node.name] = ast.dump(node)
                elif isinstance(node, ast.ClassDef):
                    unique_classes[node.name] = ast.dump(node)
        except:
            continue  # Skip the malformed chunk

    return unique_functions, unique_classes

if __name__ == '__main__':
    # Modify this list to include the paths to the files you want to analyze
    uploaded_files = [
        'your_file1.py',
        'your_file2.py',
        # ...
    ]

    # Initialize dictionaries to store all unique functions and classes from all files
    all_unique_functions = {}
    all_unique_classes = {}

    # Loop through each uploaded file and analyze it
    for file in uploaded_files:
        unique_functions, unique_classes = analyze_python_code_skip_malformed(file)

        # Update the global dictionaries with unique functions and classes from this file
        all_unique_functions.update(unique_functions)
        all_unique_classes.update(unique_classes)

    # Convert the dictionaries to lists for easier chunking
    all_unique_functions_list = list(all_unique_functions.values())
    all_unique_classes_list = list(all_unique_classes.values())

    # Chunk size (20 functions/classes per chunk for now; can be adjusted later)
    chunk_size = 20

    # Chunk the lists of all unique functions and classes
    function_chunks = [all_unique_functions_list[i:i + chunk_size] for i in range(0, len(all_unique_functions_list), chunk_size)]
    class_chunks = [all_unique_classes_list[i:i + chunk_size] for i in range(0, len(all_unique_classes_list), chunk_size)]
