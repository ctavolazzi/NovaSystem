def test_host_property(mock_requests):
    """Test the host property."""
    validator = OllamaValidator()

    # Setup successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Should return host when valid
    assert validator.host == "http://localhost:11434"  # Using default localhost