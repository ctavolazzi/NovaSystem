# map_files.py is a Python script that generates a file structure for a given directory.
# Re-implementing the updated Python script with hardcoded ignore list and other functionalities

import time
import argparse
import hashlib
import mimetypes
import subprocess
from pathlib import Path

# Function to get the SHA256 hash of a file
def get_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Function to get the git commit history for a file
def get_git_commit_history(file_path, script_dir):
    try:
        cmd = f"git log -n 3 --pretty=format:'%h - %s (%cr)' -- {file_path}"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=script_dir)
        stdout, stderr = process.communicate()
        return stdout.decode().strip() if stdout else "Not available"
    except Exception as e:
        return str(e)

# Function to check if a path is in the ignore list
def is_ignored(path, ignore_list):
    for ignore_path in ignore_list:
        if path.match(ignore_path):
            return True
    return False

import sys

def count_eligible_files(script_dir, ignore_list, include_hidden, skip_dirs):
    """ Count the number of files eligible for processing. """
    total = 0
    for path in Path(script_dir).rglob('*'):
        if path.is_dir() or is_ignored(path, ignore_list):
            continue
        if not include_hidden and path.name.startswith('.'):
            continue
        if any(skip_dir in path.parts for skip_dir in skip_dirs):
            continue
        total += 1
    return total

def update_progress_bar(total, processed):
    """ Helper function to update the progress bar. """
    progress = (processed / total) * 100
    bar_length = 50  # Length of the progress bar
    bar_filled_length = int(progress / 100 * bar_length)
    bar = "#" * bar_filled_length + "-" * (bar_length - bar_filled_length)
    sys.stdout.write(f'\rProgress: [{bar}] {int(progress)}%')
    sys.stdout.flush()




# Main function to generate file structure
def map_files(script_dir, run_name, base_output_dir='file_tree/runs',
                            include_hidden=False, deep_scan=False, verbose=False, ignore_list=None, skip_dirs=None):
    if ignore_list is None:
        ignore_list = ['archive', 'temp_files']

    if skip_dirs is None:
        skip_dirs = {'bin', 'lib', 'include', '.git', '__pycache__'}
    else:
        skip_dirs = set(skip_dirs).union({'bin', 'lib', 'include', '.git', '__pycache__'})

    output_dir = Path(base_output_dir) / run_name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'file_structure.txt'
    summary_file = output_dir / 'summary.txt'
    error_log_file = output_dir / 'error_log.txt'


    file_types = {}
    mime_types = {}
    deep_scan_details = {}

    total_files = sum(1 for path in Path(script_dir).rglob('*')
                      if not path.is_dir() and
                         not is_ignored(path, ignore_list) and
                         not (not include_hidden and path.name.startswith('.')) and
                         not any(skip_dir in path.parts for skip_dir in skip_dirs))

    processed_files = 0  # Initialize processed files count
    last_update_time = time.time()  # Initialize last update time

    for path in Path(script_dir).rglob('*'):
        if path.is_dir() or is_ignored(path, ignore_list):
            continue
        if not include_hidden and path.name.startswith('.'):
            continue
        if any(skip_dir in path.parts for skip_dir in skip_dirs):
            continue
        try:
            file_stat = path.stat()
            file_size = file_stat.st_size
            mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
            file_type = "Directory" if path.is_dir() else "File"
            mime_type = mimetypes.guess_type(path)[0] or "Unknown"

            total_files += 1
            file_types[file_type] = file_types.get(file_type, 0) + 1
            mime_types[mime_type] = mime_types.get(mime_type, 0) + 1

            if deep_scan:
                file_hash = get_file_hash(path)
                git_history = get_git_commit_history(path, script_dir)
                deep_scan_details[str(path)] = {'hash': file_hash, 'git_history': git_history}

            file_detail = f'{path.relative_to(script_dir)} - Type: {file_type} MIME: {mime_type} Size: {file_size} Modified: {mod_time}'
            with output_file.open('a') as file_out:
                file_out.write(file_detail + '\n')

            # if verbose:
            #     print(file_detail)

        except Exception as e:
            with error_log_file.open('a') as error_log:
                error_log.write(f"Error processing file {path}: {e}\n")

        processed_files += 1
        update_progress_bar(total_files, processed_files)

    update_progress_bar(total_files, total_files)

    with summary_file.open('w') as summary_out:
        summary_out.write(f'Total files processed: {total_files}\n')
        for file_type, count in file_types.items():
            summary_out.write(f'{file_type}: {count}\n')
        for mime_type, count in mime_types.items():
            summary_out.write(f'{mime_type}: {count}\n')

    if verbose and deep_scan:
        for file, details in deep_scan_details.items():
            print(f"File: {file} Hash: {details['hash']} Git History: {details['git_history']}")

    if verbose or deep_scan:
        print(f"\nSummary:")
        print(f"Total Files Processed: {total_files}")
        for file_type, count in file_types.items():
            print(f"{file_type}: {count}")
        for mime_type, count in mime_types.items():
            print(f"MIME Type '{mime_type}': {count} files")

        if deep_scan:
            print("Deep scan details available in the output files.")

    print(f"File structure generated in {output_dir}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate file structure with optional verbosity and deep scan')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-d', '--deep_scan', action='store_true', help='Enable deep scanning for additional file details')
    args = parser.parse_args()

    script_directory = Path.cwd()
    current_time = time.strftime("%Y%m%d_%H%M%S")
    map_files(script_directory, current_time, verbose=args.verbose, deep_scan=args.deep_scan)
