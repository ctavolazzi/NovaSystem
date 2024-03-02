import os
import argparse
import logging
from datetime import datetime
import zipfile
import json
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def write_to_pdf(file_data, output_file):
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    c.drawString(30, height - 30, "Extracted Code Report")

    y_position = height - 50
    for file_path, content in file_data.items():
        c.drawString(30, y_position, file_path)
        y_position -= 20
        for line in content.split('\n'):
            c.drawString(40, y_position, line)
            y_position -= 15
            if y_position < 40:
                c.showPage()
                y_position = height - 50

    c.save()

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_to_json(file_data, output_file):
    ensure_directory_exists(os.path.dirname(output_file))
    with open(output_file, 'w') as json_file:
        json.dump(file_data, json_file, indent=4)

def write_to_xml(file_data, output_file):
    ensure_directory_exists(os.path.dirname(output_file))
    root = ET.Element("files")
    for file_path, content in file_data.items():
        file_elem = ET.SubElement(root, "file", path=file_path)
        content_elem = ET.SubElement(file_elem, "content")
        content_elem.text = content

    tree = ET.ElementTree(root)
    tree.write(output_file)

def setup_logging(log_level, log_file=None):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=log_file if log_file else None,
                        level=log_level, format=log_format)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract Python code from a directory into separate files in an output folder.')
    parser.add_argument('--directory', type=str, help='Directory to scan for Python files (relative or absolute).')
    parser.add_argument('--output_folder', type=str, help='Folder to write extracted code into separate files (relative or absolute).')
    parser.add_argument('--log', type=str, help='Optional log file')
    parser.add_argument('--log_level', type=str, default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: INFO)')
    parser.add_argument('--min_size', type=int, default=0, help='Minimum file size in bytes')
    parser.add_argument('--max_size', type=int, default=None, help='Maximum file size in bytes')
    parser.add_argument('--before_date', type=str, default=None, help='Filter files modified before this date (YYYY-MM-DD)')
    parser.add_argument('--format', type=str, default='txt', choices=['txt', 'json', 'xml', 'pdf'],
                        help='Output format: txt, json, xml, or pdf (default: txt)')
    return parser.parse_args()

def is_python_file(file_path):
    return file_path.endswith('.py')

def filter_files(file_path, min_size, max_size, before_date):
    try:
        file_stat = os.stat(file_path)
        file_size = file_stat.st_size
        file_mod_time = datetime.fromtimestamp(file_stat.st_mtime)

        if (min_size is not None and file_size < min_size) or \
           (max_size is not None and file_size > max_size) or \
           (before_date is not None and file_mod_time > before_date):
            return False
        return True
    except Exception as e:
        logging.error(f"Error filtering file {file_path}: {e}")
        return False

def recursive_traverse_directory(directory, min_size, max_size, before_date):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_python_file(file_path) and filter_files(file_path, min_size, max_size, before_date):
                yield file_path

def read_file(file_path):
    try:
        with open(file_path, 'r') as infile:
            content = infile.read()
            return content
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None

def write_to_single_file(file_path, content, outfile):
    outfile.write(f"\n\n# File: {file_path}\n\n")
    outfile.write(content)

def extract_python_code(directory, output_file, min_size, max_size, before_date):
    try:
        with open(output_file, 'w') as outfile:
            for file_path in recursive_traverse_directory(directory, min_size, max_size, before_date):
                content = read_file(file_path)
                if content:
                    write_to_single_file(file_path, content, outfile)
    except Exception as e:
        logging.error(f"Error while writing to file {output_file}: {e}")

def convert_date_string(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d') if date_str else None

def zip_folder(output_folder, zip_file_name):
    try:
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, output_folder))
        logging.info(f"Folder zipped into: {zip_file_name}")
    except Exception as e:
        logging.error(f"Error zipping folder {output_folder}: {e}")

if __name__ == '__main__':
    print("Running script...")
    args = parse_arguments()
    current_dir = os.getcwd()

    # Set default for directory
    args.directory = args.directory or current_dir

    # Set default for output folder
    cwd_name = os.path.basename(current_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.output_folder = args.output_folder or os.path.join(current_dir, f"{cwd_name}_codebase_copies", f"codebase_copy_{timestamp}")

    # Ensure the output folder exists
    ensure_directory_exists(args.output_folder)

    # Generate output filename based on chosen format
    args.format = args.format or 'txt'
    output_file = os.path.join(args.output_folder, f"extracted_code_{timestamp}.{args.format}")

    setup_logging(args.log_level, args.log)

    # Convert date string to datetime object
    before_date = convert_date_string(args.before_date) if args.before_date else None

    # Process files based on the chosen format
    if args.format in ['json', 'xml', 'pdf']:
        file_data = {}
        for file_path in recursive_traverse_directory(args.directory, args.min_size, args.max_size, before_date):
            content = read_file(file_path)
            if content:
                file_data[file_path] = content

        if args.format == 'json':
            write_to_json(file_data, output_file)
        elif args.format == 'xml':
            write_to_xml(file_data, output_file)
        elif args.format == 'pdf':
            write_to_pdf(file_data, output_file)
    else:
        # Default to text format
        extract_python_code(args.directory, output_file, args.min_size, args.max_size, before_date)

    print("Script execution completed.")
