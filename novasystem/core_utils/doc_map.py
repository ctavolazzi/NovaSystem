"""
Documentation Map Generator
-------------------------
This module provides functionality to generate a map of documentation files and their contents.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union

def generate_doc_map(
    root_dir: Union[str, Path],
    file_patterns: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None
) -> Dict[str, Dict[str, Union[str, Dict]]]:
    """
    Generate a map of documentation files and their contents in a directory structure.

    Args:
        root_dir (Union[str, Path]): The root directory to start searching from
        file_patterns (Optional[List[str]]): List of file patterns to include (e.g., ["*.md", "*.rst"])
        exclude_dirs (Optional[List[str]]): List of directory names to exclude

    Returns:
        Dict[str, Dict[str, Union[str, Dict]]]: A nested dictionary representing the documentation structure
    """
    if file_patterns is None:
        file_patterns = ["*.md", "*.rst", "*.txt"]
    if exclude_dirs is None:
        exclude_dirs = [".git", "__pycache__", "node_modules", "venv", ".venv"]

    root_path = Path(root_dir)
    doc_map = {}

    def should_exclude(path: Path) -> bool:
        """Check if a path should be excluded based on exclude_dirs."""
        return any(excluded in path.parts for excluded in exclude_dirs)

    def process_directory(current_path: Path, current_map: dict) -> None:
        """Recursively process a directory and update the documentation map."""
        try:
            for item in current_path.iterdir():
                if item.is_dir():
                    if not should_exclude(item):
                        current_map[item.name] = {}
                        process_directory(item, current_map[item.name])
                else:
                    if any(item.match(pattern) for pattern in file_patterns):
                        try:
                            with open(item, 'r', encoding='utf-8') as f:
                                content = f.read()
                            current_map[item.name] = {
                                'content': content,
                                'path': str(item.relative_to(root_path)),
                                'size': os.path.getsize(item),
                                'modified': os.path.getmtime(item)
                            }
                        except Exception as e:
                            current_map[item.name] = {
                                'error': f"Failed to read file: {str(e)}",
                                'path': str(item.relative_to(root_path))
                            }
        except Exception as e:
            current_map['error'] = f"Failed to process directory: {str(e)}"

    process_directory(root_path, doc_map)
    return doc_map