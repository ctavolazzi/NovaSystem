import os
import time
import argparse
import pwd
import grp
import hashlib
import mimetypes
import subprocess

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate file structure with optional verbosity')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    return parser.parse_args()


def print_verbose(message, color_code):
    print(f"\033[{color_code}m{message}\033[0m")


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

def generate_file_structure(script_dir, run_name, base_output_dir='file_tree/runs',
                            skip_dirs=None, include_hidden=False, deep_scan=False, verbose=False):
    if skip_dirs is None:
        skip_dirs = ['bin', 'lib', 'include', 'your_lib_folder', 'archive', '.git', '__pycache__']

    output_dir = os.path.join(base_output_dir, run_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_file = os.path.join(output_dir, 'file_structure.txt')
    error_log_file = os.path.join(output_dir, 'error_log.txt')
    file_types_file = os.path.join(output_dir, 'file_types.txt')

    file_types = {}

    def update_file_types(mime_type):
        if mime_type in file_types:
            file_types[mime_type] += 1
        else:
            file_types[mime_type] = 1

    with open(output_file, 'w') as file_out, open(error_log_file, 'w') as error_log:
        for script, dirs, files in os.walk(script_dir):
            if verbose:
                print_verbose(f"Processing directory: {script}", 34)  # Verbose output
            else:
                print(".", end="", flush=True)  # Minimal output in regular mode

            if not include_hidden:
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                files = [f for f in files if not f.startswith('.')]
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            level = script.replace(script_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            file_out.write('{}{}/\n'.format(indent, os.path.basename(script)))

            subindent = ' ' * 4 * (level + 1)
            for f in files:
                file_path = os.path.join(script, f)
                if verbose:
                    print_verbose(f"Processing file: {file_path}", 32)  # Move this line inside the verbose check
                try:
                    file_stat = os.stat(file_path)
                    file_size = format_file_size(file_stat.st_size)
                    mod_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime))
                    file_type = get_file_type(file_path)
                    mime_type = get_mime_type(file_path)
                    update_file_types(mime_type)
                    file_hash = get_file_hash(file_path) if deep_scan else "N/A"
                    git_history = get_git_commit_history(file_path, script_dir) if deep_scan else "N/A"

                    if deep_scan:
                        create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_ctime))
                        access_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_atime))
                        permissions = get_file_permissions(file_path)
                        user, group = get_file_owner(file_path)
                        file_out.write(f'{subindent}{f} - Type: {file_type}, MIME: {mime_type}, Size: {file_size}, '
                                       f'Hash: {file_hash}, Git History: {git_history}, Modified: {mod_time}, '
                                       f'Created: {create_time}, Accessed: {access_time}, Permissions: {permissions}, '
                                       f'Owner: {user}, Group: {group}\n')
                    else:
                        file_out.write(f'{subindent}{f} - Type: {file_type}, MIME: {mime_type}, Size: {file_size}, '
                                       f'Last Modified: {mod_time}\n')

                except Exception as e:
                    if verbose:
                        print_verbose(f"Error processing file {file_path}: {e}", 31)  # Error message only in verbose mode
                    error_log.write(f"Error processing file {file_path}: {e}\n")
            if not verbose:
              print(".", end="", flush=True)  # Minimal output in regular mode

    with open(file_types_file, 'w') as f:
        for mime_type, count in file_types.items():
            f.write(f"{mime_type}: {count}\n")

if __name__ == '__main__':
    args = parse_arguments()
    verbose = args.verbose

    script_directory = os.getcwd()
    current_time = time.strftime("%Y%m%d_%H%M%S")
    run_name = f'run_{current_time}'
    root_directory = script_directory

    if verbose:
        print("Running in verbose mode...")
    else:
        print("Generating file structure...")

    generate_file_structure(script_directory, run_name, deep_scan=verbose)
