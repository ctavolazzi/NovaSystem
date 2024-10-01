# Ultimate File Explorer (UFE)

The Ultimate File Explorer (UFE) is a powerful Python script designed to recursively scan directories, collect extensive metadata, and generate comprehensive reports in both JSON and HTML formats. With features like file hashing, duplicate detection, and customizable output, UFE is an invaluable tool for exploring and analyzing your file system.

## Table of Contents

- [Ultimate File Explorer (UFE)](#ultimate-file-explorer-ufe)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Method 1: Install as a Command-Line Tool](#method-1-install-as-a-command-line-tool)
    - [Method 2: Use the Script Directly](#method-2-use-the-script-directly)
  - [Usage](#usage)
    - [Basic Usage](#basic-usage)
    - [Command-Line Arguments](#command-line-arguments)
    - [Examples](#examples)
      - [Scan a Specific Directory](#scan-a-specific-directory)
      - [Include Hidden Files and Calculate Hashes](#include-hidden-files-and-calculate-hashes)
      - [Limit Scanning Depth](#limit-scanning-depth)
      - [Output Both JSON and HTML Reports](#output-both-json-and-html-reports)
      - [Detect Duplicate Files](#detect-duplicate-files)
  - [HTML Report](#html-report)
  - [Customization](#customization)
    - [Modifying Default Arguments](#modifying-default-arguments)
    - [Adding New Features](#adding-new-features)
    - [Improving the HTML Template](#improving-the-html-template)
  - [Error Handling](#error-handling)
  - [Cross-Platform Compatibility](#cross-platform-compatibility)
    - [Platform-Specific Notes](#platform-specific-notes)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Recursive Directory Scanning**: Explore directories and subdirectories to any depth.
- **Extensive Metadata Collection**:
  - File permissions
  - Owner and group information
  - File sizes (human-readable and bytes)
  - Creation, modification, and access times
  - MIME types
- **File Hashing**: Calculate MD5 and SHA-256 hashes for files.
- **Duplicate Detection**: Identify duplicate files based on hashes.
- **Output Formats**:
  - **JSON**: Structured data for further processing.
  - **HTML**: Interactive and customizable reports.
- **Customizable Parameters**: Control scanning depth, inclusion of hidden files, and more.
- **Error Handling**: Logs and reports errors encountered during scanning.

## Prerequisites

- **Python 3.6 or higher** is required.
- **pip**: Python package manager for installing dependencies.

## Installation

### Method 1: Install as a Command-Line Tool

1. **Clone the Repository** (or download the script files):

   ```bash
   git clone https://github.com/yourusername/ultimate-file-explorer.git
   cd ultimate-file-explorer
   ```

2. **Install the Package**:

   ```bash
   pip install .
   ```

   This installs UFE and its dependencies, making the `ufe` command available system-wide.

### Method 2: Use the Script Directly

1. **Download the Script**:

   Save the `ultimate_file_explorer.py` script to a directory of your choice.

2. **Install Dependencies**:

   ```bash
   pip install aiofiles jinja2 tqdm humanize psutil
   ```

   For Windows users:

   ```bash
   pip install python-magic-bin==0.4.14
   ```

   For Unix/Linux users:

   ```bash
   pip install python-magic
   ```

## Usage

### Basic Usage

To run UFE with default settings:

```bash
ufe --output-html report.html
```

Or, if you're using the script directly:

```bash
python ultimate_file_explorer.py --output-html report.html
```

### Command-Line Arguments

- `--path`: Path to scan (default is the current directory).
- `--include-hidden`: Include hidden files and directories.
- `--max-depth`: Maximum depth to scan (unlimited if not specified).
- `--output-json`: Output JSON file name.
- `--output-html`: Output HTML file name.
- `--hashes`: Calculate MD5 and SHA-256 hashes for files.
- `--detect-duplicates`: Detect duplicate files based on SHA-256 hashes.

### Examples

#### Scan a Specific Directory

```bash
ufe --path "/path/to/directory" --output-html report.html
```

#### Include Hidden Files and Calculate Hashes

```bash
ufe --include-hidden --hashes --output-html report.html
```

#### Limit Scanning Depth

```bash
ufe --max-depth 2 --output-html report.html
```

#### Output Both JSON and HTML Reports

```bash
ufe --output-json data.json --output-html report.html
```

#### Detect Duplicate Files

```bash
ufe --detect-duplicates --output-html report.html
```

## HTML Report

The HTML report provides an interactive view of your file system:

- **Tree Structure**: Visual representation of directories and files.
- **Metadata Display**: View detailed information about each file and directory.
- **Duplicate Files Section**: Lists detected duplicates with their paths.
- **Error Logs**: Displays any errors encountered during scanning.

To customize the appearance and content of the HTML report, you can modify the `template.html` file included with the script.

## Customization

### Modifying Default Arguments

Edit the `parse_args()` function in the script to change default values for arguments.

### Adding New Features

Enhance the script by implementing additional functionalities, such as:

- Filtering files by extension or size.
- Integrating with other tools or APIs.
- Extending metadata collection.

### Improving the HTML Template

Customize the `template.html` file to:

- Change the layout and styles.
- Add new sections or visualizations.
- Incorporate JavaScript libraries for enhanced interactivity.

## Error Handling

- **Error Logging**: Errors encountered during scanning are collected and can be viewed in the console output and HTML report.
- **Common Errors**:
  - **Permission Errors**: Occur when the script lacks permission to access certain files or directories.
  - **File Read Errors**: Issues with reading file contents, possibly due to corruption.

Ensure you have appropriate permissions and consider running the script with elevated privileges if necessary.

## Cross-Platform Compatibility

- **Windows Support**: The script is compatible with Windows, with adjustments for modules like `pwd` and `grp` which are not available on Windows systems.
- **Unix/Linux Support**: Fully supported, with access to all features.

### Platform-Specific Notes

- **File Ownership**: On Windows, the script uses `os.getlogin()` to retrieve the current user as the owner.
- **Magic Library**: Uses `python-magic-bin` on Windows and `python-magic` on Unix/Linux for MIME type detection.

## Contributing

Contributions are welcome! Feel free to:

- Report bugs or suggest features via GitHub issues.
- Submit pull requests for improvements or fixes.
- Share the script and help others discover its capabilities.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Enjoy exploring your file system with the Ultimate File Explorer! If you have any questions or need assistance, feel free to reach out.**