import os
import json
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from utils.ollama_validator import OllamaValidator

class TestValidatorSuite:
    @pytest.fixture
    def setup_data_directory(self):
        """Create a permanent data directory for test results."""
        data_dir = Path("test_data")
        data_dir.mkdir(exist_ok=True)

        # Create subdirectories for different types of data
        (data_dir / "reports").mkdir(exist_ok=True)
        (data_dir / "logs").mkdir(exist_ok=True)

        return data_dir

    @pytest.fixture
    def mock_requests(self):
        """Mock requests with configurable responses."""
        with patch('requests.get') as mock_get:
            yield mock_get

    def generate_test_scenarios(self):
        """Generate different test scenarios."""
        return [
            {
                'name': 'normal_operation',
                'status_code': 200,
                'response': {'version': '0.1.0'},
                'expected_valid': True,
                'delay': 0
            },
            {
                'name': 'slow_response',
                'status_code': 200,
                'response': {'version': '0.1.0'},
                'expected_valid': True,
                'delay': 2
            },
            {
                'name': 'service_error',
                'status_code': 500,
                'response': {'error': 'Internal Server Error'},
                'expected_valid': False,
                'delay': 0
            },
            {
                'name': 'connection_timeout',
                'exception': TimeoutError("Connection timed out"),
                'expected_valid': False,
                'delay': 0
            }
        ]

    def test_validation_suite(self, setup_data_directory, mock_requests):
        """Run a comprehensive validation test suite."""
        scenarios = self.generate_test_scenarios()
        test_results = []

        # Create a timestamp for this test run
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        for scenario in scenarios:
            print(f"\nRunning scenario: {scenario['name']}")

            # Configure mock response based on scenario
            if 'exception' in scenario:
                mock_requests.side_effect = scenario['exception']
            else:
                mock_response = MagicMock()
                mock_response.status_code = scenario['status_code']
                mock_response.json.return_value = scenario['response']
                mock_requests.return_value = mock_response

            # Add artificial delay if specified
            if scenario['delay'] > 0:
                time.sleep(scenario['delay'])

            # Run validation
            validator = OllamaValidator()
            start_time = time.time()
            is_valid = validator.is_valid
            end_time = time.time()

            # Collect results
            result = {
                'scenario': scenario['name'],
                'timestamp': datetime.now().isoformat(),
                'duration': end_time - start_time,
                'is_valid': is_valid,
                'expected_valid': scenario['expected_valid'],
                'host': validator._host,
                'test_passed': is_valid == scenario['expected_valid']
            }

            test_results.append(result)
            print(f"Result: {'✅' if result['test_passed'] else '❌'} "
                  f"(took {result['duration']:.2f}s)")

        # Generate detailed report
        report = {
            'test_run': timestamp,
            'total_scenarios': len(scenarios),
            'passed_scenarios': sum(1 for r in test_results if r['test_passed']),
            'total_duration': sum(r['duration'] for r in test_results),
            'results': test_results
        }

        # Save report
        report_file = setup_data_directory / "reports" / f"validation_suite_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nTest Suite Summary:")
        print(f"Total Scenarios: {report['total_scenarios']}")
        print(f"Passed Scenarios: {report['passed_scenarios']}")
        print(f"Total Duration: {report['total_duration']:.2f}s")
        print(f"Report saved to: {report_file}")

        # Verify all tests passed
        assert report['passed_scenarios'] == report['total_scenarios'], \
            f"Only {report['passed_scenarios']} out of {report['total_scenarios']} scenarios passed"

    def test_repeated_validation(self, setup_data_directory, mock_requests):
        """Test repeated validation with varying conditions."""
        num_iterations = 10
        results = []

        print(f"\nRunning {num_iterations} validation iterations")

        for i in range(num_iterations):
            # Alternate between success and failure
            if i % 3 == 0:  # Every third iteration fails
                mock_requests.side_effect = Exception("Random failure")
            else:
                mock_requests.side_effect = None  # Clear previous side effect
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"version": "0.1.0"}
                mock_requests.return_value = mock_response

            validator = OllamaValidator()
            start_time = time.time()  # Add timing
            is_valid = validator.is_valid
            end_time = time.time()

            result = {
                'iteration': i + 1,
                'timestamp': datetime.now().isoformat(),
                'duration': end_time - start_time,
                'is_valid': is_valid,
                'host': validator._host,
                'expected_valid': (i % 3 != 0)  # Expected to be valid when not every third
            }
            results.append(result)

            print(f"Iteration {i+1}: {'✅' if result['is_valid'] else '❌'} "
                  f"(took {result['duration']:.2f}s)")

            time.sleep(0.1)  # Small delay between iterations

        # Save results with more details
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = setup_data_directory / "reports" / f"repeated_validation_{timestamp}.json"

        report = {
            'test_run': timestamp,
            'total_iterations': num_iterations,
            'successful_validations': sum(1 for r in results if r['is_valid']),
            'expected_successes': sum(1 for r in results if r['expected_valid']),
            'accuracy': sum(1 for r in results if r['is_valid'] == r['expected_valid']) / num_iterations,
            'total_duration': sum(r['duration'] for r in results),
            'average_duration': sum(r['duration'] for r in results) / num_iterations,
            'results': results
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nRepeated Validation Summary:")
        print(f"Total Iterations: {report['total_iterations']}")
        print(f"Successful Validations: {report['successful_validations']}")
        print(f"Expected Successes: {report['expected_successes']}")
        print(f"Accuracy: {report['accuracy']:.2%}")
        print(f"Average Duration: {report['average_duration']:.3f}s")
        print(f"Report saved to: {report_file}")

        # Verify the accuracy is 100%
        assert report['accuracy'] == 1.0, \
            f"Test accuracy was {report['accuracy']:.2%}, expected 100%"