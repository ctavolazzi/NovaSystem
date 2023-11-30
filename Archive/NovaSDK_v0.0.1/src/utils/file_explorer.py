from pathlib import Path
import argparse
import os

class FileExplorer:
    def __init__(self, script_dir):
        self.current_dir = Path(script_dir).resolve()

    def navigate_to_directory(self, directory):
        new_dir = self.current_dir / directory
        if new_dir.is_dir():
            self.current_dir = new_dir
            return f"Moved to {new_dir}"
        else:
            return "Invalid directory or path does not exist."

    def list_directory_contents(self):
        try:
            contents = [f"{p.name}{'/' if p.is_dir() else ''}" for p in self.current_dir.iterdir()]
            return "\n".join(contents)
        except PermissionError:
            return "Permission denied."

    def view_file(self, file_path, lines=10):
        try:
            file_to_view = self.current_dir / file_path
            if file_to_view.is_file():
                with file_to_view.open('r') as file:
                    for _ in range(lines):
                        line = file.readline()
                        if not line:
                            break
                        print(line, end='')
                    if not file.readline() == '':
                        print("\n[File continues...]")
            else:
                return "File does not exist."
        except PermissionError:
            return "Permission denied."

    def navigate_up(self):
        parent_dir = self.current_dir.parent
        if parent_dir != self.current_dir:  # Check to avoid navigating above root
            self.current_dir = parent_dir

# Command-line interface
def prompt_for_directory():
    user_input = input("Enter the path of the directory to explore (or hit Enter for current directory): ").strip()
    return user_input if user_input else os.getcwd()

def main():
    parser = argparse.ArgumentParser(description="File Explorer")
    parser.add_argument("-d", "--directory", help="Directory to start the exploration", required=False)
    args = parser.parse_args()

    directory = args.directory or prompt_for_directory()
    explorer = FileExplorer(directory)

    while True:
        print("\nCurrent Directory:", explorer.current_dir)
        choice = input("1: List\n2: View\n3: Navigate\n4: Up\n5: Exit\nChoose an option: ")

        if choice == '1':
            print(explorer.list_directory_contents())
        elif choice == '2':
            file_name = input("Enter file name to view: ")
            print(explorer.view_file(file_name))
        elif choice == '3':
            dir_name = input("Enter directory name to navigate: ")
            print(explorer.navigate_to_directory(dir_name))
        elif choice == '4':
            explorer.navigate_up()
        elif choice == '5':
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()