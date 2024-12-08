import os
import json
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
from tqdm import tqdm  # For progress bars

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

from utils.ollama_validator import OllamaValidator

class ValidationRunner:
    def __init__(self, validators, scenarios):
        self.validators = validators
        self.scenarios = scenarios
        self.results = []
        self.report_dir = Path("validation_data/reports")
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def run_all_validations(self):
        """Run all validation scenarios."""
        total_scenarios = len(self.scenarios)
        total_duration = 0
        passed_scenarios = 0

        print("\n📋 Starting Validation Suite")
        print("==================================================")

        for i, (scenario_name, scenario) in enumerate(self.scenarios.items(), 1):
            print(f"\n[{i}/{total_scenarios}] ▶️  Running scenario: {scenario_name}")

            start_time = time.time()
            result = scenario(self.validators)
            duration = time.time() - start_time
            total_duration += duration

            if result.get('success', False):
                passed_scenarios += 1
                print(f"Result: ✅ (took {duration:.2f}ms)")
            else:
                print(f"Result: ❌ (took {duration:.2f}ms)")
                if 'error' in result:
                    print(f"Error: {result['error']}")

            self.results.append({
                'scenario': scenario_name,
                'success': result.get('success', False),
                'duration': duration,
                'error': result.get('error', None)
            })

        self._save_report()
        self._print_summary(total_scenarios, passed_scenarios, total_duration)

    def simulate_delay(self, seconds):
        """Simulate a delay with a progress bar."""
        with tqdm(total=100,
                 desc="⏳ Simulating delay",
                 bar_format='{desc} |{bar}| {percentage:3.0f}%',
                 ncols=70,
                 leave=False) as pbar:
            for i in range(100):
                time.sleep(seconds/100)
                pbar.update(1)

    def _save_report(self):
        """Save validation results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.report_dir / f"validation_suite_{timestamp}.json"

        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'results': self.results
            }, f, indent=2)

        print(f"\nReport saved to: {report_file}")

    def _print_summary(self, total, passed, duration):
        """Print validation suite summary."""
        print("\n📊 Test Suite Summary")
        print("==================================================")
        print(f"Total Scenarios: {total}")
        print(f"Passed Scenarios: {passed}")
        print(f"Total Duration: {duration:.3f}s")
        print(f"Average Duration: {(duration/total):.2f}ms")

        if passed == total:
            print("\n✨ All validations passed successfully!")

def main():
    """Main entry point for the validation runner."""
    runner = ValidationRunner()
    try:
        report = runner.run_validation_suite()
        success = report['passed_scenarios'] == report['total_scenarios']
        exit_code = 0 if success else 1

        if success:
            print(f"\n{Colors.GREEN}✨ All validations passed successfully!{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}⚠️  Some validations failed. Check the report for details.{Colors.ENDC}")

        return exit_code
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error running validation suite: {str(e)}{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    exit(main())