import os
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from utils.ollama_validator import OllamaValidator

class TestValidatorIterations:
    @pytest.fixture
    def setup_log_directory(self, tmp_path):
        """Create a temporary log directory for testing."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()
        return log_dir

    @pytest.fixture
    def mock_requests(self):
        """Mock requests to avoid actual network calls."""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"version": "0.1.0"}
            mock_get.return_value = mock_response
            yield mock_get

    def test_multiple_validation_cycles(self, setup_log_directory, mock_requests):
        """Test running multiple validation cycles and logging results."""
        print(f"\nLog directory: {setup_log_directory}")
        num_iterations = 5
        results = []

        validator = OllamaValidator()

        # Run validation cycles
        for i in range(num_iterations):
            result = {
                'iteration': i + 1,
                'timestamp': datetime.now().isoformat(),
                'host': validator.host,
                'is_valid': validator.is_valid,
            }
            results.append(result)

        # Generate report file
        report_file = setup_log_directory / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Verify results
        assert len(results) == num_iterations
        for result in results:
            assert result['is_valid'] == True
            assert 'host' in result
            assert 'timestamp' in result

        # Verify report file exists and is valid JSON
        assert report_file.exists()
        with open(report_file) as f:
            loaded_results = json.load(f)
            assert len(loaded_results) == num_iterations

    def test_validation_with_service_interruption(self, setup_log_directory, mock_requests):
        """Test validation cycles with simulated service interruptions."""
        num_iterations = 5
        results = []

        validator = OllamaValidator()

        # Simulate service interruptions on alternate iterations
        for i in range(num_iterations):
            if i % 2 == 0:
                mock_requests.side_effect = Exception("Connection error")
            else:
                mock_requests.side_effect = None
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"version": "0.1.0"}
                mock_requests.return_value = mock_response

            result = {
                'iteration': i + 1,
                'timestamp': datetime.now().isoformat(),
                'host': validator._host,
                'is_valid': validator.is_valid,
            }
            results.append(result)

        # Generate report file
        report_file = setup_log_directory / f"interruption_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Verify results alternate between valid and invalid
        assert len(results) == num_iterations
        for i, result in enumerate(results):
            assert result['is_valid'] == (i % 2 != 0)

        # Verify report file exists and is valid JSON
        assert report_file.exists()
        with open(report_file) as f:
            loaded_results = json.load(f)
            assert len(loaded_results) == num_iterations