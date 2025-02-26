#!/usr/bin/env python3
"""
Diagnostic script to identify import path issues in the NovaSystem package.
"""

import sys
import site
import os
import importlib.util

print("=== Python Environment Diagnostics ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print("\n=== Import Paths ===")
print(f"sys.path:")
for idx, path in enumerate(sys.path):
    print(f"  {idx}. {path}")

print("\n=== Site Packages ===")
site_packages = site.getsitepackages()
print(f"Site packages:")
for sp in site_packages:
    print(f"  {sp}")

print("\n=== Package Location Search ===")
print(f"Looking for 'novasystem' package:")
for path in sys.path:
    potential_module = os.path.join(path, "novasystem")
    potential_init = os.path.join(potential_module, "__init__.py")

    if os.path.isdir(potential_module):
        if os.path.isfile(potential_init):
            print(f"  ✅ {potential_module} (valid package with __init__.py)")
        else:
            print(f"  ⚠️  {potential_module} (directory exists but no __init__.py)")
    else:
        print(f"  ❌ {potential_module} (not found)")

print("\n=== Egg Link Check ===")
egg_link_path = None
for sp in site_packages:
    potential_egg_link = os.path.join(sp, "novasystem.egg-link")
    if os.path.isfile(potential_egg_link):
        egg_link_path = potential_egg_link
        with open(potential_egg_link, 'r') as f:
            egg_link_content = f.read().strip()
        print(f"Found egg-link at: {potential_egg_link}")
        print(f"Egg-link content: {egg_link_content}")

        # Check if the path in egg-link exists
        if os.path.isdir(egg_link_content.split('\n')[0]):
            print(f"✅ Path in egg-link exists")
        else:
            print(f"❌ Path in egg-link does NOT exist")

if not egg_link_path:
    print("No novasystem.egg-link found in site-packages")

print("\n=== Entry Point Check ===")
try:
    # Try to import the cli module
    print("Attempting to import novasystem.cli:")
    spec = importlib.util.find_spec("novasystem.cli")
    if spec:
        print(f"✅ Found at: {spec.origin}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'main'):
            print(f"✅ 'main' function exists in the module")
        else:
            print(f"❌ No 'main' function in the module")
    else:
        print("❌ Module not found")
except Exception as e:
    print(f"❌ Error importing module: {e}")

print("\n=== Directory Structure ===")
project_root = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {project_root}")

print("\nDirectories in project root:")
for item in os.listdir(project_root):
    if os.path.isdir(os.path.join(project_root, item)):
        print(f"  {item}/")

# Check for the nested structure issue
nested_novasystem = os.path.join(project_root, "NovaSystem")
if os.path.isdir(nested_novasystem):
    print(f"\nContents of nested 'NovaSystem' directory:")
    for item in os.listdir(nested_novasystem):
        item_path = os.path.join(nested_novasystem, item)
        if os.path.isdir(item_path):
            print(f"  {item}/")
        elif os.path.isfile(item_path) and item.endswith('.py'):
            print(f"  {item}")

# Check for lowercase novasystem
lower_novasystem = os.path.join(project_root, "novasystem")
if os.path.isdir(lower_novasystem):
    print(f"\nContents of 'novasystem' directory:")
    for item in os.listdir(lower_novasystem):
        item_path = os.path.join(lower_novasystem, item)
        if os.path.isdir(item_path):
            print(f"  {item}/")
        elif os.path.isfile(item_path) and item.endswith('.py'):
            print(f"  {item}")