"""
NovaSystem Demos

This module dynamically imports and manages demonstration scripts for NovaSystem.
"""

import os
import importlib
import glob
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Dynamically import demo scripts
demo_scripts = glob.glob(os.path.join(os.path.dirname(__file__), "demo_*.py"))
available_demos = {}

for script in demo_scripts:
    script_name = os.path.basename(script)[:-3]  # Remove '.py'
    try:
        demo_module = importlib.import_module('.' + script_name, package='demos')
        available_demos[script_name] = {
            "function": getattr(demo_module, 'run_demo', None),
            "description": getattr(demo_module, '__doc__', "No description available.")
        }
    except ImportError as e:
        logging.error(f"Failed to import {script_name}: {e}")

def run_demo(demo_name):
    """
    Run a specified demo from the available demos.

    Parameters:
    demo_name (str): The name of the demo to run.
    """
    try:
        demo = available_demos[demo_name]
        logging.info(f"Running demo: {demo_name}")
        print(demo["description"])
        demo["function"]()
    except KeyError:
        logging.error(f"No demo found with the name: {demo_name}")
    except Exception as e:
        logging.error(f"Error occurred while running demo {demo_name}: {e}")

# Example usage: run_demo("demo_stc")
