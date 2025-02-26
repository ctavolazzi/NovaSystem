#!/usr/bin/env python3
"""
Documentation Map Generator

This script generates a visual map of the NovaSystem documentation structure
to help users navigate through the documentation.

Usage:
    python scripts/generate_doc_map.py > docs/doc_map.md
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configuration
ROOT_DIR = Path("docs")
OUTPUT_FILE = Path("docs/doc_map.md")
IGNORE_PATTERNS = [
    r"^\..*",  # Hidden files
    r".*\.pyc$",  # Python cache files
    r"__pycache__",  # Python cache directories
]
MAX_DEPTH = 3  # Maximum depth to display in the map

def should_ignore(path: str) -> bool:
    """Check if a path should be ignored."""
    for pattern in IGNORE_PATTERNS:
        if re.match(pattern, os.path.basename(path)):
            return True
    return False

def extract_title(file_path: Path) -> str:
    """Extract the title from a Markdown file."""
    if not file_path.exists() or not file_path.is_file():
        return file_path.name

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Just read the first 500 chars to find the title

            # Look for the first Markdown heading
            match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if match:
                return match.group(1)

            # If no heading found, use the filename
            return file_path.stem.replace('-', ' ').title()
    except Exception:
        return file_path.stem.replace('-', ' ').title()

def get_dir_description(dir_path: Path) -> str:
    """Get description for a directory from its README.md file."""
    readme_path = dir_path / "README.md"
    if readme_path.exists():
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 chars

                # Get the title first
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else dir_path.name

                # Try to extract the first paragraph after the title
                paragraphs = re.findall(r'^# .+\n\n(.+?)(\n\n|$)', content, re.MULTILINE | re.DOTALL)
                if paragraphs:
                    return f"{title} - {paragraphs[0][0].replace(chr(10), ' ')}"
                return title
        except Exception:
            pass

    return dir_path.name.replace('-', ' ').title()

def generate_tree(
    start_path: Path,
    current_depth: int = 0,
    is_last: bool = True,
    prefix: str = ""
) -> List[str]:
    """Generate a tree representation of the documentation structure."""
    if current_depth > MAX_DEPTH:
        return [f"{prefix}{'└── ' if is_last else '├── '}..."]

    if start_path.is_file():
        if start_path.name == "README.md":
            return []  # Skip README.md files in the tree view

        title = extract_title(start_path)
        file_indicator = f"{prefix}{'└── ' if is_last else '├── '}"
        rel_path = start_path.relative_to(ROOT_DIR)
        return [f"{file_indicator}[{title}]({rel_path})"]

    # It's a directory
    lines = []
    if current_depth > 0:  # Skip the root directory name
        dir_desc = get_dir_description(start_path)
        dir_indicator = f"{prefix}{'└── ' if is_last else '├── '}"
        lines.append(f"{dir_indicator}**{dir_desc}**")
        new_prefix = f"{prefix}{'    ' if is_last else '│   '}"
    else:
        new_prefix = prefix

    # Get sorted items in the directory
    items = sorted([
        p for p in start_path.iterdir()
        if not should_ignore(p.name)
    ], key=lambda p: (p.is_file(), p.name))

    # Process each item
    for i, item in enumerate(items):
        is_last_item = (i == len(items) - 1)
        lines.extend(generate_tree(item, current_depth + 1, is_last_item, new_prefix))

    return lines

def generate_index(start_path: Path) -> Dict[str, List[Tuple[str, str]]]:
    """Generate an alphabetical index of documentation files."""
    index = {}

    # Walk through all files
    for root, dirs, files in os.walk(start_path):
        # Skip directories that match ignore patterns
        dirs[:] = [d for d in dirs if not should_ignore(d)]

        for file in files:
            if file.endswith('.md') and file != "README.md" and not should_ignore(file):
                file_path = Path(os.path.join(root, file))
                title = extract_title(file_path)
                rel_path = file_path.relative_to(ROOT_DIR)

                # Add to index by first letter
                first_char = title[0].upper()
                if first_char not in index:
                    index[first_char] = []
                index[first_char].append((title, str(rel_path)))

    # Sort each section
    for key in index:
        index[key] = sorted(index[key], key=lambda x: x[0].lower())

    return dict(sorted(index.items()))

def generate_category_index(start_path: Path) -> Dict[str, List[Tuple[str, str]]]:
    """Generate a category-based index of documentation files."""
    categories = {}

    # Define top-level directories as categories
    for item in start_path.iterdir():
        if item.is_dir() and not should_ignore(item.name):
            category_name = get_dir_description(item)
            categories[category_name] = []

            # Walk through all files in this category
            for root, dirs, files in os.walk(item):
                # Skip directories that match ignore patterns
                dirs[:] = [d for d in dirs if not should_ignore(d)]

                for file in files:
                    if file.endswith('.md') and file != "README.md" and not should_ignore(file):
                        file_path = Path(os.path.join(root, file))
                        title = extract_title(file_path)
                        rel_path = file_path.relative_to(ROOT_DIR)
                        categories[category_name].append((title, str(rel_path)))

    # Sort items within each category
    for category in categories:
        categories[category] = sorted(categories[category], key=lambda x: x[0].lower())

    return dict(sorted(categories.items()))

def generate_search_tips() -> str:
    """Generate search tips section."""
    return """
## Search Tips

To quickly find what you need in this documentation:

1. **Use your browser's search:** Press `Ctrl+F` (or `Cmd+F` on Mac) and enter keywords related to what you're looking for.

2. **Common search terms:**
   - For agent-related information, search: "agent", "DCE", "CAE", "expert"
   - For memory-related information, search: "memory", "vector", "context"
   - For process-related information, search: "process", "orchestration", "template"
   - For API-related information, search: "API", "endpoint", "WebSocket"

3. **GitHub search:** When viewing on GitHub, you can search the entire repository using the search bar at the top.
"""

def main():
    """Generate the documentation map."""
    # Create the file content
    content = [
        "# NovaSystem Documentation Map",
        "",
        "This document provides a navigational map of the NovaSystem documentation.",
        "",
        "## Documentation Tree",
        "",
    ]

    # Generate tree structure
    content.extend(generate_tree(ROOT_DIR))

    # Generate category index
    content.append("")
    content.append("## Documentation by Category")
    content.append("")

    category_index = generate_category_index(ROOT_DIR)
    for category, items in category_index.items():
        content.append(f"### {category}")
        content.append("")
        for title, path in items:
            content.append(f"- [{title}]({path})")
        content.append("")

    # Generate alphabetical index
    content.append("## Alphabetical Index")
    content.append("")

    alpha_index = generate_index(ROOT_DIR)
    for letter, items in alpha_index.items():
        content.append(f"### {letter}")
        content.append("")
        for title, path in items:
            content.append(f"- [{title}]({path})")
        content.append("")

    # Add search tips
    content.append(generate_search_tips())

    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

    print(f"Documentation map generated at {OUTPUT_FILE}")

if __name__ == "__main__":
    main()