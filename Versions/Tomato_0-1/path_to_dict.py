import os
import json

def path_to_dict(path):
    name = os.path.basename(path)
    if os.path.isdir(path):
        return {name: [path_to_dict(os.path.join(path, child)) for child in os.listdir(path)]}
    else:
        return name

def main():
    root_dir = os.getcwd()  # Or replace with the path to your root directory
    structure = path_to_dict(root_dir)

    with open('structure.json', 'w') as f:
        json.dump(structure, f, indent=4)

if __name__ == "__main__":
    main()
