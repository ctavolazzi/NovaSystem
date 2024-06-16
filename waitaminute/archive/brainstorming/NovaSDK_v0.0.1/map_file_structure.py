import os
import time
import argparse
import pwd
import grp
import hashlib
import mimetypes
import subprocess
import stat
from pathlib import Path

from src.utils.stream_to_console import stc



def get_file_details(file_path):
    """
    Retrieves comprehensive details about a file.

    Args:
    file_path (str): Path to the file.

    Returns:
    dict: A dictionary containing various file details.
    """
    try:
        # Basic file stats
        stats = os.stat(file_path)
        file_info = {
            "size": stats.st_size,
            "last_modified": time.ctime(stats.st_mtime),
            "last_accessed": time.ctime(stats.st_atime),
            "created": time.ctime(stats.st_ctime)
        }

        # Owner and permissions
        file_info["owner"] = stat.filemode(stats.st_mode)
        file_info["uid"] = stats.st_uid
        file_info["gid"] = stats.st_gid

        # File hash for integrity
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as file:
            buf = file.read()
            hasher.update(buf)
        file_info["hash"] = hasher.hexdigest()

        # Additional details based on file type
        if file_path.endswith('.py'):  # Example for Python files
            with open(file_path, 'r') as file:
                lines = file.readlines()
                file_info["line_count"] = len(lines)
                # Additional Python-specific analysis can be done here

        return file_info

    except Exception as e:
        return {"error": str(e)}


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate file structure with optional verbosity and deep scan')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-d', '--deep_scan', action='store_true', help='Enable deep scanning for additional file details')
    return parser.parse_args()

def print_verbose(message, status):
    if status == "info":
        # Green for file details, blue for summary headers
        parts = message.split(":")
        colored_message = "\033[32m" + parts[0] + "\033[0m" if len(parts) == 1 else "\033[34m" + parts[0] + ":\033[32m" + ":".join(parts[1:]) + "\033[0m"
        print(colored_message)
    else:
        # Default colors for other statuses
        color_code = "32" if status == "success" else "31"
        print(f"\033[{color_code}m{message}\033[0m")

def print_verbose_info(message):
    # Blue color for variable content
    print(f"\033[34m{message}\033[0m", end="")

def print_verbose_label(message):
    # Grey color for non-variable text
    print(f"\033[90m{message}\033[0m", end="")

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"

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

def print_summary(total_files, file_types, mime_types):
    print_verbose("File summary:", "info")

    # Print the summary details directly from the variables, not from the file
    print_verbose(f"Total files processed: \033[34m{total_files}\033[32m", "info")
    print_verbose("File types distribution:", "info")
    for f_type, count in file_types.items():
        print_verbose(f"  \033[32m{f_type}: \033[34m{count}\033[32m", "info")
    print_verbose("MIME types distribution:", "info")
    for m_type, count in mime_types.items():
        print_verbose(f"  \033[32m{m_type}: \033[34m{count}\033[32m", "info")
    print('')

def print_deep_scan_summary(deep_scan_details):
    if deep_scan_details:  # Check if there are any deep scan details
        print_verbose("Deep scan details:", "info")
        for file_path, details in deep_scan_details.items():
            detail_parts = [color_text(f"File: {os.path.basename(file_path)}", 34)]
            for key, value in details.items():
                detail_parts.append(color_text(f"{key.capitalize()}: {value}", 34))
            print_verbose(", ".join(detail_parts), "info")
        print('')


def generate_file_structure(script_dir, run_name, base_output_dir='file_tree/runs',
                            skip_dirs=None, include_hidden=False, deep_scan=False, verbose=False):
    if skip_dirs is None:
        skip_dirs = ['bin', 'lib', 'include', 'your_lib_folder', 'archive', '.git', '__pycache__']

    output_dir = os.path.join(base_output_dir, run_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, 'file_structure.txt')
    summary_file = os.path.join(output_dir, 'summary.txt')
    error_log_file = os.path.join(output_dir, 'error_log.txt')

    total_files = 0
    file_types = {}
    mime_types = {}
    deep_scan_details = {}

    def update_distributions(file_type, mime_type):
        nonlocal total_files, file_types, mime_types
        total_files += 1
        file_types[file_type] = file_types.get(file_type, 0) + 1
        mime_types[mime_type] = mime_types.get(mime_type, 0) + 1

    with open(output_file, 'w') as file_out, open(summary_file, 'w') as summary_out, open(error_log_file, 'w') as error_log:
        for root, dirs, files in os.walk(script_dir):
            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for f in files:
                file_path = os.path.join(root, f)
                try:
                    file_stat = os.stat(file_path)
                    file_size = format_file_size(file_stat.st_size)
                    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
                    file_type = get_file_type(file_path)
                    mime_type = get_mime_type(file_path)
                    update_distributions(file_type, mime_type)

                    if deep_scan:
                        file_hash = get_file_hash(file_path) if deep_scan else "N/A"
                        git_history = get_git_commit_history(file_path, script_dir) if deep_scan else "N/A"
                        deep_scan_details[file_path] = {'hash': file_hash, 'git_history': git_history}

                    file_detail = f'{os.path.join(root.replace(script_dir, ""), f)} - Type: {file_type} MIME: {mime_type} Size: {file_size}'
                    file_out.write(f'{file_detail} | {deep_scan_details} Modified: {mod_time}\n')

                    if verbose:
                        print_verbose_label("Name: ")
                        print_verbose_info(f"{os.path.basename(file_path)}, ")
                        print_verbose_label("Type: ")
                        print_verbose_info(f"{file_type} ")
                        print_verbose_label("MIME: ")
                        print_verbose_info(f"{mime_type} ")
                        print_verbose_label("Size: ")
                        print_verbose_info(f"{file_size} ")
                        print_verbose_label("Last Modified: ")
                        print_verbose_info(f"{mod_time} ")
                        if deep_scan:
                            for file_path, details in deep_scan_details.items():
                                detail_parts = [color_text(f"File: {os.path.basename(file_path)}", 34)]
                                for key, value in details.items():
                                    detail_parts.append(color_text(f"{key.capitalize()}: {value}", 34))
                                print_verbose(", ".join(detail_parts), "info")
                        print('')

                except Exception as e:
                    error_log.write(f"Error processing file {file_path}: {e}\n")
                    if verbose:
                        print_verbose(f"\rError processing file {file_path}: {e}", "error")

        summary_out.write(f'Total files processed: {total_files}\n')
        summary_out.write('File types distribution:\n')
        for f_type, count in file_types.items():
            summary_out.write(f'  {f_type}: {count}\n')
        summary_out.write('MIME types distribution:\n')
        for m_type, count in mime_types.items():
            summary_out.write(f'  {m_type}: {count}\n')


        if deep_scan:
            print_verbose("Deep scan details:", "info")
            for file, details in deep_scan_details.items():
                print_verbose(f"\033[32mFile: \033[34m{file}\033[32m Hash: \033[34m{details['hash']}\033[32m Git History: \033[34m{details['git_history']}\033[32m", "info")

        if verbose:
            print_verbose(f"\rFile structure generation complete. Total files processed: {total_files}", "success")
            print_summary(total_files, file_types, mime_types)

        if verbose and deep_scan:
            print_deep_scan_summary(deep_scan_details)

        # At the end, just print the total files processed
        print(f"File map complete. Total files processed: {total_files}")

if __name__ == '__main__':
    args = parse_arguments()
    verbose = args.verbose
    deep_scan = args.deep_scan
    script_directory = os.getcwd()
    current_time = time.strftime("%Y%m%d_%H%M%S")
    run_name = f'run_{current_time}'
    generate_file_structure(script_directory, run_name, deep_scan=deep_scan, verbose=verbose)
