from tqdm import tqdm
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
            stdout, stderr = process.communicate()
            return stdout.decode().strip() if stdout else "Not available"
        except Exception as e:
            return str(e)

    def is_ignored(self, path):
        """ Check if a path is in the ignore list. """
        for ignore_path in self.ignore_list:
            if path.match(ignore_path):
                return True
        return False

    def map_files(self, run_name, base_output_dir='file_tree/runs', target_dir=None, include_hidden=False, deep_scan=False, verbose=False):
        """ Map the files in a directory. """
        if not target_dir:
          current_dir = Path.cwd()
          print(f"Current directory: {current_dir}")
          choice = input("Do you want to map the current directory? (Y/n): ").strip().lower()
          if choice in ['n', 'no']:
              self.script_dir = Path(input("Enter the path of the directory to map: ").strip())
          else:
              self.script_dir = current_dir
        else:
            self.script_dir = Path(target_dir)

        print("\n=== File Processing Start in {} ===\n".format(self.script_dir.resolve()))

        print("\n=== File Processing Start ===\n")
        output_dir = self.script_dir / base_output_dir / run_name
        output_dir.mkdir(parents=True, exist_ok=True)

        file_types = {}
        mime_types = {}
        deep_scan_details = {}
        file_details = []

        total_files = sum(1 for path in self.script_dir.rglob('*')
                          if not path.is_dir() and
                             not self.is_ignored(path) and
                             not (not include_hidden and path.name.startswith('.')) and
                             not any(skip_dir in path.parts for skip_dir in self.skip_dirs))

        # processed_files = 0
        # last_update_time = time.time()

        # with tqdm(total=total_files, desc="Processing Files", unit="file", leave=True) as pbar:
        #   for path in self.script_dir.rglob('*'):
        #       if path.is_dir() or self.is_ignored(path):
        #           continue
        #       if not include_hidden and path.name.startswith('.'):
        #           continue
        #       if any(skip_dir in path.parts for skip_dir in self.skip_dirs):
        #           continue

        #       try:
        #           file_stat = path.stat()
        #           file_size = file_stat.st_size
        #           mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
        #           file_type = "Directory" if path.is_dir() else "File"
        #           mime_type = mimetypes.guess_type(path)[0] or "Unknown"

        #           file_types[file_type] = file_types.get(file_type, 0) + 1
        #           mime_types[mime_type] = mime_types.get(mime_type, 0) + 1

        #           if deep_scan:
        #               file_hash = self.get_file_hash(path)
        #               git_history = self.get_git_commit_history(path, self.script_dir)
        #               deep_scan_details[str(path)] = {'hash': file_hash, 'git_history': git_history}

        #           if verbose:
        #               file_detail = f'{path.relative_to(self.script_dir)} - Type: {file_type} MIME: {mime_type} Size: {file_size} Modified: {mod_time}'
        #               print(file_detail)


        #       except Exception as e:
        #           print(f"\nError processing file {path}: {e}")

        #       processed_files += 1
        #       # self.update_progress_bar(total_files, processed_files, last_update_time)
        #       pbar.update(1)

        # Use tqdm for the progress bar
        for path in tqdm(self.script_dir.rglob('*'), total=total_files, unit='file', desc="Processing Files"):
            if path.is_dir() or self.is_ignored(path):
                continue
            if not include_hidden and path.name.startswith('.'):
                continue
            if any(skip_dir in path.parts for skip_dir in self.skip_dirs):
                continue
            try:
                file_stat = path.stat()
                file_size = file_stat.st_size
                mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
                file_type = "Directory" if path.is_dir() else "File"
                mime_type = mimetypes.guess_type(path)[0] or "Unknown"

                file_types[file_type] = file_types.get(file_type, 0) + 1
                mime_types[mime_type] = mime_types.get(mime_type, 0) + 1

                if deep_scan:
                    file_hash = self.get_file_hash(path)
                    git_history = self.get_git_commit_history(path, self.script_dir)
                    deep_scan_details[str(path)] = {'hash': file_hash, 'git_history': git_history}

                if verbose:
                    file_detail = f'{path.relative_to(self.script_dir)} - Type: {file_type} MIME: {mime_type} Size: {file_size} Modified: {mod_time}'
                    file_details.append(file_detail)
                    print(file_detail)
            except Exception as e:
                print(f"\nError processing file {path}: {e}")

        # self.update_progress_bar(total_files, total_files, last_update_time)
        print("\n\n=== File Processing Complete ===\n")

        if deep_scan:
            print("=== Deep Scan Details ===\n")
            for file, details in deep_scan_details.items():
                print(f"File: {file} Hash: {details['hash']} Git History: {details['git_history']}")

        if verbose:
            print("\n=== File Details ===\n")
            for file_detail in file_details:
                print(file_detail)

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

# This part will be removed or modified as this script is now designed to be imported.
if __name__ == '__main__':
    # Example usage of the FileMapper class

    # Define the directory to map files in (replace with an actual directory path)
    test_directory = "src"

    # Instantiate the FileMapper class
    file_mapper = FileMapper(test_directory)

    # Run the file mapping process
    # Set 'run_name' to a unique identifier, like a timestamp or a specific tag
    run_name = time.strftime("%Y%m%d_%H%M%S")
    file_mapper.map_files(run_name, verbose=True, deep_scan=True)

    # This will print the file structure to the console and create relevant files in the specified directory
