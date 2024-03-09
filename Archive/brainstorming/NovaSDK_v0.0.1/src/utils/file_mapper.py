# srs/utils/file_mapper.py
# Description: A Python script that maps a file structure for a given directory.
# Use: python3 file_mapper.py -d <directory> -o <output_dir> -n <run_name> -v -s -i -r

from tqdm import tqdm
import argparse
import time
import hashlib
import mimetypes
import subprocess
import sys
from pathlib import Path

class FileMapper:
    def __init__(self, script_dir, ignore_list=None, skip_dirs=None):
        self.script_dir = Path(script_dir)
        self.ignore_list = ignore_list if ignore_list else ['archive', 'temp_files']
        self.skip_dirs = set(skip_dirs).union({'bin', 'lib', 'include', '.git', '__pycache__'}) if skip_dirs else {'bin', 'lib', 'include', '.git', '__pycache__'}

    @staticmethod
    def get_file_hash(file_path):
        """ Calculate the SHA256 hash of a file. """
        sha256_hash = hashlib.sha256()
        with file_path.open("rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def get_git_commit_history(file_path, script_dir):
        """ Get the git commit history for a file. """
        try:
            cmd = f"git log -n 3 --pretty=format:'%h - %s (%cr)' -- {file_path}"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=script_dir)
            stdout = process.communicate()
            return stdout.decode().strip() if stdout else "Not available"
        except Exception as e:
            return str(e)

    def is_ignored(self, path):
        """ Check if a path is in the ignore list. """
        for ignore_path in self.ignore_list:
            if path.match(ignore_path):
                return True
        return False

    def write_file_details(self, output_dir, file_types, mime_types, deep_scan_details, verbose, deep_scan):
        with open(output_dir / 'file_details.txt', 'w') as file:
            file.write("=== Summary ===\n")
            file.write(f"Total Files Processed: {sum(file_types.values())}\n")
            for file_type, count in file_types.items():
                file.write(f"File Type '{file_type}': {count} files\n")
            for mime_type, count in mime_types.items():
                file.write(f"MIME Type '{mime_type}': {count} files\n")

            if verbose:
                file.write("\n=== File Details ===\n")
                # Write verbose details

            if deep_scan:
                file.write("\n=== Deep Scan Details ===\n")
                for file_path, details in deep_scan_details.items():
                    file.write(f"File: {file_path} Hash: {details['hash']} Git History: {details['git_history']}\n")


    def map_files(self, run_name, base_output_dir='file_tree/runs', target_dir=None, include_hidden=False, deep_scan=False, verbose=False):
        """ Map the files in a directory. """
        if not target_dir:
          current_dir = Path.cwd()
          print(f"Current directory: {current_dir}")
          choice = input("Do you want to map the current directory? (Y/n): ").strip().lower()
          if choice in ['n', 'no']:
              self.script_dir = Path(input("Enter the path of the directory to map: ").strip())
          else:
              print(f"Invalid input. Mapping the current directory: {current_dir}")
              self.script_dir = current_dir
        else:
            self.script_dir = Path(target_dir)

        print("\n=== File Processing Start in {} ===\n".format(self.script_dir.resolve()))

        output_dir = self.script_dir / base_output_dir / run_name
        output_dir.mkdir(parents=True, exist_ok=True)

        file_types = {}
        mime_types = {}
        deep_scan_details = {}
        # file_details = []

        total_files = sum(1 for path in self.script_dir.rglob('*')
                          if not path.is_dir() and
                             not self.is_ignored(path) and
                             not (not include_hidden and path.name.startswith('.')) and
                             not any(skip_dir in path.parts for skip_dir in self.skip_dirs))

        # Use tqdm for the progress bar
        with tqdm(total=total_files, desc="Processing Files", unit="file", leave=True) as pbar:

            for path in self.script_dir.rglob('*'):
                if path.is_dir() or self.is_ignored(path):
                    continue
                if not include_hidden and path.name.startswith('.'):
                    continue
                if any(skip_dir in path.parts for skip_dir in self.skip_dirs):
                    continue

                pbar.set_description(f"Processing {path.name}")

                try:
                    file_stat = path.stat()
                    file_size = file_stat.st_size
                    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
                    file_type = "Directory" if path.is_dir() else "File"
                    mime_type = mimetypes.guess_type(path)[0] or "Unknown"

                    pbar.set_postfix(file_type=file_type, mime_type=mime_type, file_size=file_size, mod_time=mod_time)

                    file_types[file_type] = file_types.get(file_type, 0) + 1
                    mime_types[mime_type] = mime_types.get(mime_type, 0) + 1

                    if deep_scan:
                        file_hash = self.get_file_hash(path)
                        git_history = self.get_git_commit_history(path, self.script_dir)
                        deep_scan_details[str(path)] = {'hash': file_hash, 'git_history': git_history}


                except Exception as e:
                    tqdm.write(f"\nError processing file {path}: {e}")

                pbar.update(1)
        # Call write_file_details after processing all files
        self.write_file_details(output_dir, file_types, mime_types, deep_scan_details, verbose, deep_scan)

        # self.update_progress_bar(total_files, total_files, last_update_time)
        print("\n\n=== File Processing Complete ===\n")

        if deep_scan:
            print("=== Deep Scan Details ===\n")
            # for file, details in deep_scan_details.items():
            #     print(f"File: {file} Hash: {details['hash']} Git History: {details['git_history']}")

        if verbose:
            print("\n=== File Details ===\n")
            # for file_detail in file_details:
            #     print(file_detail)

        print("\n=== Summary ===\n")
        print(f"Total Files Processed: {total_files}")
        for file_type, count in file_types.items():
            print(f"File Type '{file_type}': {count} files")
        for mime_type, count in mime_types.items():
            print(f"MIME Type '{mime_type}': {count} files")

    @staticmethod
    def update_progress_bar(total, processed, last_update_time):
        """ Helper function to update the progress bar. """
        if total > 0:
            progress = (processed / total) * 100
            bar_length = 50  # Length of the progress bar
            bar_filled_length = int(progress / 100 * bar_length)
            bar = "#" * bar_filled_length + "-" * (bar_length - bar_filled_length)
            sys.stdout.write(f'\rProgress: [{bar}] {int(progress)}%   ')
            sys.stdout.flush()
        else:
            print("\rNo files to process.", end='')

def prompt_for_input(arg, message, default=None):
    if arg not in sys.argv:
        user_input = input(message)
        return user_input if user_input else default
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Map a file structure for a given directory.')

    # Define arguments
    parser.add_argument('-d', '--directory', help='Directory to map')
    parser.add_argument('-o', '--output', help='Output directory')
    parser.add_argument('-n', '--name', help='Run name')
    parser.add_argument('-v', '--verbose', help='Verbose output', action='store_true')
    parser.add_argument('-s', '--deep_scan', help='Perform a deep scan', action='store_true')
    parser.add_argument('-i', '--include_hidden', help='Include hidden files', action='store_true')

    # Parse arguments
    args, unknown = parser.parse_known_args()

    # Prompt for missing arguments with defaults
    directory = args.directory or prompt_for_input('-d', 'Enter the path of the directory to map (or hit Enter for current directory): ', default=str(Path.cwd()))
    output = args.output or prompt_for_input('-o', 'Enter the output directory (or hit Enter for default): ', default='file_tree/runs')
    name = args.name or prompt_for_input('-n', 'Enter the run name (or hit Enter for timestamp): ', default=time.strftime("%Y%m%d_%H%M%S"))

    # Instantiate and run FileMapper
    file_mapper = FileMapper(directory)
    file_mapper.map_files(name, base_output_dir=output, target_dir=directory,
                          include_hidden=args.include_hidden, deep_scan=args.deep_scan,
                          verbose=args.verbose)