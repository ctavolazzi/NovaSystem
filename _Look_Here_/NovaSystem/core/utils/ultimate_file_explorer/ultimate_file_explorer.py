#!/usr/bin/env python3
import os
import sys
import datetime
import random
import string
import platform
import argparse
import re
from pathlib import Path
from stat import filemode
import hashlib

# External libraries
try:
    import humanize
except ImportError:
    print("Error: 'humanize' package is not installed. Please install it using 'pip install humanize'.")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
except ImportError:
    print("Error: 'colorama' package is not installed. Please install it using 'pip install colorama'.")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("Error: 'tqdm' package is not installed. Please install it using 'pip install tqdm'.")
    sys.exit(1)

try:
    import pathspec
except ImportError:
    print("Error: 'pathspec' package is not installed. Please install it using 'pip install pathspec'.")
    sys.exit(1)

# Handle magic library separately due to OS differences
try:
    import magic
except ImportError:
    if platform.system() == 'Windows':
        print("Error: 'magic' package is not installed. Please install 'python-magic-bin' using 'pip install python-magic-bin==0.4.14'.")
    else:
        print("Error: 'magic' package is not installed. Please install 'python-magic' using 'pip install python-magic'.")
    sys.exit(1)

# Initialize colorama for colored output
init(autoreset=True)

# Conditional imports for Unix-specific modules
if platform.system() != 'Windows':
    import pwd
    import grp

# Global variables for statistics and error logging
errors = []
file_count = 0
directory_count = 0

def sanitize_filename(s):
    """
    Sanitize a string to be a valid filename by replacing invalid characters with underscores.

    Args:
        s (str): The string to sanitize.

    Returns:
        str: The sanitized string.
    """
    invalid_chars = r'[<>:"/\\|?*\'"]'
    sanitized = re.sub(invalid_chars, '_', s)
    return sanitized

def generate_file_name(base_name="directory_map", mapped_path=None):
    """Generate a file name based on the mapped path and current timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if mapped_path:
        dir_name = Path(mapped_path).name
        filename = f"{base_name}_{dir_name}_{timestamp}.txt"
    else:
        filename = f"{base_name}_{timestamp}.txt"
    
    return filename

def get_mapping_choice():
    """
    Prompt the user to choose between mapping ALL files or SOME files.

    Returns:
        str: 'ALL' or 'SOME' based on the user's choice.
    """
    while True:
        choice = input("Do you want to map ALL files or SOME files? (Enter 'A' for ALL, 'S' for SOME): ").strip().upper()
        if choice == 'A':
            return 'ALL'
        elif choice == 'S':
            return 'SOME'
        else:
            print(f"{Fore.RED}Invalid input. Please enter 'A' for ALL or 'S' for SOME.{Style.RESET_ALL}")

def load_ignore_patterns(ignore_file_path):
    """
    Load ignore patterns from a specified ignore file.
    
    Args:
        ignore_file_path (Path): The path to the ignore file.
    
    Returns:
        list: A list of ignore patterns.
    """
    patterns = []
    ignore_file = Path(ignore_file_path)
    if ignore_file.exists():
        try:
            with ignore_file.open('r', encoding='utf-8') as f:
                patterns = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
            print(f"{Fore.GREEN}Loaded ignore patterns from '{ignore_file}'.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error reading ignore file '{ignore_file}': {e}{Style.RESET_ALL}")
            errors.append(f"Error reading ignore file '{ignore_file}': {e}")
    else:
        print(f"{Fore.YELLOW}No ignore file found at '{ignore_file}'. No patterns will be ignored.{Style.RESET_ALL}")
    return patterns

def get_file_info(entry):
    """Get detailed information about a file."""
    file_info = {}
    try:
        stat_info = entry.stat()
        file_info['size'] = stat_info.st_size
        file_info['modified'] = datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        file_info['permissions'] = filemode(stat_info.st_mode)
        
        if platform.system() != 'Windows':
            file_info['owner'] = pwd.getpwuid(stat_info.st_uid).pw_name
            file_info['group'] = grp.getgrgid(stat_info.st_gid).gr_name
        else:
            file_info['owner'] = 'N/A'
            file_info['group'] = 'N/A'
        
        file_info['type'] = magic.from_file(entry.path, mime=True)
        
        # Calculate file hash
        with open(entry.path, "rb") as f:
            file_hash = hashlib.md5()
            chunk = f.read(8192)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(8192)
        file_info['md5'] = file_hash.hexdigest()
        
    except Exception as e:
        return f"Error getting file info: {str(e)}"
    
    return file_info

def get_directory_info(path, exclude_spec, progress_bar, root_path):
    global errors, file_count, directory_count
    tree = {}
    try:
        for entry in os.scandir(path):
            progress_bar.update(1)  # Update progress without changing description

            relative_path = os.path.relpath(entry.path, root_path)
            if exclude_spec.match_file(relative_path):
                continue

            try:
                if entry.is_dir(follow_symlinks=False):
                    directory_count += 1
                    tree[entry.name] = get_directory_info(entry.path, exclude_spec, progress_bar, root_path)
                elif entry.is_symlink():
                    tree[entry.name] = f"Symbolic Link -> {os.readlink(entry.path)}"
                else:
                    file_count += 1
                    tree[entry.name] = get_file_info(entry)
            except Exception as e:
                error_msg = f"Error processing {entry.path}: {str(e)}"
                errors.append(error_msg)
                progress_bar.write(error_msg)

    except Exception as e:
        error_msg = f"Error accessing directory {path}: {str(e)}"
        errors.append(error_msg)
        progress_bar.write(error_msg)

    return tree

def print_directory_tree(tree, indent=''):
    """
    Print the directory tree structure.

    Args:
        tree (dict): The directory tree structure.
        indent (str): The current indentation level.
    """
    for key, value in tree.items():
        if isinstance(value, dict):
            if 'size' in value:
                # It's a file
                print(f"{indent}{key} - {humanize.naturalsize(value['size'])}, modified {value['modified']}, type {value['type']}")
            else:
                # It's a directory
                print(f"{indent}{key}/")
                print_directory_tree(value, indent + '    ')
        else:
            # It's an error message or symbolic link
            print(f"{indent}{key} - {value}")

def format_full_path(path):
    """
    Format the full path for better readability.
    For Windows paths, replace backslashes with forward slashes for consistency.
    """
    return str(path).replace('\\', '/')

def main():
    global errors, file_count, directory_count, args

    parser = argparse.ArgumentParser(description='Scan a directory and generate a directory map.')
    parser.add_argument('path', nargs='?', default='.', help='Directory path to scan (default: current directory)')
    parser.add_argument('-o', '--output', help='Output file name (default: generated based on timestamp)')
    parser.add_argument('-e', '--exclude', action='append', default=[], help='Patterns to exclude')
    parser.add_argument('-q', '--quiet', action='store_true', help='Do not print the directory map to console')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print detailed information during scanning')
    args = parser.parse_args()


    start_path = Path(args.path).resolve()
    if not start_path.exists():
        print(f"{Fore.RED}Error: The path '{start_path}' does not exist.{Style.RESET_ALL}")
        sys.exit(1)

    if not args.quiet:
        print(f"Scanning directory: {start_path}")

    # Get mapping choice from user
    mapping_choice = get_mapping_choice()

    exclude_patterns = []

    if mapping_choice == 'SOME':
        # Load ignore patterns from the specified ignore file
        ignore_file_path = Path("C:/Users/ctavo/OneDrive/Desktop/Code/GitHub/NovaSystem/_Look_Here_/NovaSystem/core/utils/ultimate_file_explorer/.ufeignore")
        exclude_patterns = load_ignore_patterns(ignore_file_path)
    else:
        # No ignore patterns for 'ALL' choice
        exclude_patterns = []

    # Add patterns from command-line arguments
    exclude_patterns.extend(args.exclude)

    # Compile the patterns using pathspec
    exclude_spec = pathspec.PathSpec.from_lines('gitwildmatch', exclude_patterns)

    # Define the output directory
    output_dir = Path.cwd() / 'maps'
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            if not args.quiet:
                print(f"{Fore.GREEN}Created output directory '{output_dir}'.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error creating output directory '{output_dir}': {e}{Style.RESET_ALL}")
            sys.exit(1)

    # Estimate total items for the progress bar
    total_items = sum(len(files) + len(dirs) for _, dirs, files in os.walk(start_path))

    # Initialize progress bar with a simple description
    with tqdm(total=total_items, unit='item', ncols=100, disable=args.quiet) as progress_bar:
        progress_bar.set_description("Scanning")  # Set a simple, static description
        tree = get_directory_info(start_path, exclude_spec, progress_bar, start_path)

    # Generate output file name with mapped path
    output_file = generate_file_name(mapped_path=start_path)
    output_file = output_dir / output_file

    # Save the directory map to a file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Add the full directory path at the top of the file with improved formatting
            formatted_path = format_full_path(start_path)
            f.write(f"Full directory path: {formatted_path}\n")
            f.write("=" * (len(formatted_path) + 22) + "\n\n")  # Underline for emphasis
            
            # Redirect standard output to the file
            original_stdout = sys.stdout
            sys.stdout = f
            print_directory_tree(tree)
            sys.stdout = original_stdout
    except Exception as e:
        print(f"{Fore.RED}Error writing to file '{output_file}': {e}{Style.RESET_ALL}")
        sys.exit(1)

    if not args.quiet:
        print(f"\nDirectory map saved to '{output_file}'")
        print(f"Total files: {file_count}")
        print(f"Total directories: {directory_count}")

    # Save errors to a log file if any
    if errors:
        error_log = output_dir / 'ufe_errors.log'
        try:
            with open(error_log, 'w', encoding='utf-8') as f:
                for error in errors:
                    f.write(f"{error}\n")
            if not args.quiet:
                print(f"\n{Fore.YELLOW}Encountered {len(errors)} errors. See '{error_log}' for details.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error writing to error log '{error_log}': {e}{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
