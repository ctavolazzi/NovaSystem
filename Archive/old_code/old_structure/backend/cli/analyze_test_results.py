#!/usr/bin/env python
"""
Command-line tool for analyzing test results using the FailureAnalyzer.

This script takes test output from a file or standard input and generates
a report with failure analysis and recommendations.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
script_path = Path(__file__).absolute()
backend_path = script_path.parent.parent  # This is the backend directory
sys.path.insert(0, str(backend_path))  # Add backend to the path

# Import from the agents module directly since we're now at the backend level
from agents.analysis.failure_analyzer import (
    FailureAnalyzer,
    TestFramework
)

def setup_logging(verbose=False):
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze test results and generate recommendations."
    )

    parser.add_argument(
        "--input-file", "-i",
        type=str,
        help="Path to the file containing test output. If not provided, reads from stdin."
    )

    parser.add_argument(
        "--output-file", "-o",
        type=str,
        help="Path to write the analysis report. If not provided, writes to stdout."
    )

    parser.add_argument(
        "--project-type", "-p",
        type=str,
        default="python",
        choices=["python", "node", "java", "unknown"],
        help="Type of project being analyzed. Default: python"
    )

    parser.add_argument(
        "--framework", "-f",
        type=str,
        choices=[f.value for f in TestFramework],
        help="Test framework used. If not provided, auto-detected."
    )

    parser.add_argument(
        "--format", "-fmt",
        type=str,
        default="markdown",
        choices=["json", "html", "markdown"],
        help="Output format for the report. Default: markdown"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()

def main():
    """Main entry point for the script."""
    args = parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("Starting test result analysis...")

    # Read input
    if args.input_file:
        logger.info(f"Reading test output from file: {args.input_file}")
        try:
            with open(args.input_file, 'r') as f:
                test_output = f.read()
        except Exception as e:
            logger.error(f"Error reading input file: {e}")
            return 1
    else:
        logger.info("Reading test output from stdin...")
        test_output = sys.stdin.read()

    # Create analyzer and process the test output
    analyzer = FailureAnalyzer(project_type=args.project_type)
    logger.info(f"Analyzing test output for project type: {args.project_type}")

    try:
        analysis_result = analyzer.analyze_test_output(
            test_output,
            framework=args.framework
        )

        if not analysis_result["success"]:
            logger.error(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}")
            return 1

        # Generate report
        logger.info(f"Generating {args.format} report...")
        report = analyzer.generate_report(analysis_result, format=args.format)

        # Write output
        if args.output_file:
            logger.info(f"Writing report to file: {args.output_file}")
            try:
                with open(args.output_file, 'w') as f:
                    f.write(report)
            except Exception as e:
                logger.error(f"Error writing output file: {e}")
                return 1
        else:
            print(report)

        # Log summary
        logger.info(
            f"Analysis complete. Found {len(analysis_result['failures'])} failures "
            f"using {analysis_result['framework']} framework."
        )
        return 0

    except Exception as e:
        logger.exception(f"Error during analysis: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())