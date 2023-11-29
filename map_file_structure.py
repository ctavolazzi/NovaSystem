import os
import time
import argparse
import pwd
import grp
import hashlib
import mimetypes
import subprocess
from src.utils.stream_to_console import stc

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate file structure with optional verbosity')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    return parser.parse_args()

def print_verbose(message, status):
    color_code = "32" if status == "success" else "31"  # Green for success, red for error
    # Properly format the message with color coding
    formatted_message = f"\033[{color_code}m{message}\033[0m"
    print(formatted_message, end="\r")


def format_file_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f}{unit}"
        size /= 1024

def get_file_permissions(file_path):
    permissions = oct(os.stat(file_path).st_mode)[-3:]
    return permissions

def get_file_owner(file_path):
    uid = os.stat(file_path).st_uid
    gid = os.stat(file_path).st_gid
    user = pwd.getpwuid(uid).pw_name
    group = grp.getgrgid(gid).gr_name
    return user, group

def get_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_type(file_path):
    if os.path.islink(file_path):
        return "Symbolic Link"
    elif os.path.isdir(file_path):
        return "Directory"
    elif os.path.isfile(file_path):
        return "File"
    else:
        return "Other"

def get_mime_type(file_path):
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type if mime_type else "Unknown"

def get_git_commit_history(file_path, script_dir):
    try:
        cmd = f"git log -n 3 --pretty=format:'%h - %s (%cr)' -- {file_path}"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=script_dir)
        stdout, stderr = process.communicate()
        return stdout.decode().strip() if stdout else "Not available"
    except Exception as e:
        return str(e)

def map_file_structure(script_dir, run_name, base_output_dir='file_tree/runs',
                            skip_dirs=None, include_hidden=False, deep_scan=False, verbose=False):
    if skip_dirs is None:
        skip_dirs = ['bin', 'lib', 'include', 'your_lib_folder', 'archive', '.git', '__pycache__']

    output_dir = os.path.join(base_output_dir, run_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, 'file_structure.txt')
    summary_file = os.path.join(output_dir, 'summary.txt')
    error_log_file = os.path.join(output_dir, 'error_log.txt')
    file_types_file = os.path.join(output_dir, 'file_types.txt')

    file_types = {}
    mime_types = {}
    total_files = 0

    def update_distributions(file_type, mime_type):
        file_types[file_type] = file_types.get(file_type, 0) + 1
        mime_types[mime_type] = mime_types.get(mime_type, 0) + 1

    def update_file_types(mime_type):
        if mime_type in file_types:
            file_types[mime_type] += 1
        else:
            file_types[mime_type] = 1

    max_line_length = 0

    with open(output_file, 'w') as file_out, open(summary_file, 'w') as summary_out, open(error_log_file, 'w') as error_log:
        for script, dirs, files in os.walk(script_dir):
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for f in files:
                file_path = os.path.join(script, f)
                try:
                    total_files += 1
                    update_distributions(get_file_type(file_path), get_mime_type(file_path))
                    file_stat = os.stat(file_path)
                    file_size = format_file_size(file_stat.st_size)
                    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
                    file_type = get_file_type(file_path)
                    mime_type = get_mime_type(file_path)
                    update_file_types(mime_type)
                    file_hash = get_file_hash(file_path) if deep_scan else "N/A"
                    git_history = get_git_commit_history(file_path, script_dir) if deep_scan else "N/A"

                    # Writing details to output and summary files
                    file_detail = f'{os.path.join(script.replace(script_dir, ""), f)} - Type: {file_type}, MIME: {mime_type}, Size: {file_size}'
                    file_out.write(f'{file_detail}, Hash: {file_hash}, Git History: {git_history}, Modified: {mod_time}\n')

                    if verbose:
                        # Dynamic single-line verbose output
                        line_to_print = f"\r{file_detail}"
                        if len(line_to_print) < max_line_length:
                            # Pad the line if it is shorter than the longest line printed so far
                            line_to_print = line_to_print.ljust(max_line_length)
                        else:
                            # Update max_line_length if the current line is longer
                            max_line_length = len(line_to_print)

                        print_verbose(line_to_print, "success")

                except Exception as e:
                    error_log.write(f"Error processing file {file_path}: {e}\n")
                    if verbose:
                        print_verbose(f"\rError processing file {file_path}: {e}", "error")
                    else:
                        print(f"\rError processing file {file_path}: {e}")

        # Write summary to summary file and print to console
        summary_content = f'Total files processed: {total_files}\n'
        summary_content += 'File types distribution:\n'
        for f_type, count in file_types.items():
            summary_content += f'  {f_type}: {count}\n'
        summary_content += 'MIME types distribution:\n'
        for m_type, count in mime_types.items():
            summary_content += f'  {m_type}: {count}\n'

        # Write summary to the summary file
        summary_out.write(summary_content)

        # Verbose mode output
        if verbose:
            print("\nFile structure generation complete.")
            print("\nSummary of files processed:")
            print(summary_content)
        # Non-verbose mode output
        else:
            print(f"File structure generation complete. Total files processed: {total_files}")


    with open(file_types_file, 'w') as f:
        for mime_type, count in file_types.items():
            f.write(f"{mime_type}: {count}\n")

if __name__ == '__main__':
    args = parse_arguments()
    verbose = args.verbose
    script_directory = os.getcwd()
    current_time = time.strftime("%Y%m%d_%H%M%S")
    run_name = f'run_{current_time}'
    map_file_structure(script_directory, run_name, deep_scan=verbose, verbose=verbose)
