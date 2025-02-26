# Test Maintenance Guide

**Date:** May 30, 2024
**Developer:** Claude & User

## Purpose

This guide provides best practices for maintaining the test suite based on insights gained during the [test suite fixes](test_suite_fixes.md) and [debugging process](debugging_techniques.md).

## Best Practices for Test Maintenance

### 1. Model Name Management

The codebase uses LLM model names in various places. To maintain consistency:

- **Use Constants**: Define model names as constants in a central location
  ```python
  # utils/constants.py
  OLLAMA_DEFAULT_MODEL = "llama3"
  OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
  ```

- **Import Constants**: Always import these constants rather than hardcoding model names
  ```python
  from utils.constants import OLLAMA_DEFAULT_MODEL

  class AutogenSetup:
      def __init__(self, model_name=None):
          self.model_name = model_name or OLLAMA_DEFAULT_MODEL
  ```

- **Update Process**: When updating model names, use this checklist:
  1. Update the constant value
  2. Run all tests with verbose output (`pytest -v`)
  3. Fix any assertion errors related to expected model names
  4. Check both test fixtures and assertions

### 2. Mock Object Design

When creating mock objects for testing:

- **Faithfully Simulate Behavior**: Ensure mocks accurately represent the behavior of real objects
  ```python
  class MockHub:
      async def start_discussion(self, topic):
          # Simulate the real hub's validation logic
          if not topic:
              raise ValueError("Topic cannot be empty")
          return "mock-discussion-id"
  ```

- **Include Error Cases**: Always implement error cases in mocks
  ```python
  class FailingMockHub:
      async def start_discussion(self, topic):
          # Simulate failure conditions
          if "fail" in topic.lower():
              raise ValueError("Simulated failure for testing")
          return "mock-discussion-id"
  ```

- **Document Mock Behavior**: Add comments explaining how mocks differ from real implementations
  ```python
  class MockAgent:
      """
      Simplified mock of an agent that only returns predefined responses.
      Does not implement the full message handling of real agents.
      """
  ```

### 3. Error Handling Tests

To ensure robust error handling:

- **Test Happy Paths AND Error Paths**: Always include tests for error conditions
  ```python
  @pytest.mark.asyncio
  async def test_error_handling():
      # Test successful case
      result = await process_valid_input()
      assert result == expected_success

      # Test error case
      with pytest.raises(ValueError):
          await process_invalid_input()
  ```

- **Verify Error Propagation**: Check that errors are properly caught and handled
  ```python
  @pytest.mark.asyncio
  async def test_error_propagation():
      task_id = queue.add_task("failing_task", function_that_will_fail)
      await queue.process_queue()
      status = queue.get_task_status(task_id)
      assert status["status"] == "failed"
      assert "error" in status
  ```

### 4. Addressing Deprecation Warnings

Handle deprecation warnings proactively:

- **Update Deprecated APIs**: Replace deprecated code with recommended alternatives
  ```python
  # DEPRECATED
  SwarmResult.update_forward_refs()

  # RECOMMENDED
  SwarmResult.model_rebuild()
  ```

- **Filter Specific Warnings in Tests**: Use pytest's warning filter for third-party warnings
  ```python
  # In pytest.ini
  [pytest]
  filterwarnings =
      ignore::PydanticDeprecatedSince20
      ignore::asyncio.PytestDeprecationWarning
  ```

### 5. Test Performance

To maintain efficient tests:

- **Use Appropriate Timeouts**: Set reasonable timeouts for async tests
  ```python
  @pytest.mark.asyncio
  @pytest.mark.timeout(5)  # 5 second timeout
  async def test_quick_operation():
      # Test code here
  ```

- **Mock External Services**: Use mocks for tests that would otherwise call external services
  ```python
  @patch('openai.resources.chat.completions.AsyncCompletions.create')
  async def test_with_mocked_openai(mock_create):
      mock_create.return_value = MockResponse(content="Test response")
      # Test code here
  ```

### 6. Common Test Failures and Solutions

| Failure Pattern | Likely Cause | Solution |
|-----------------|--------------|----------|
| `expected None, got {'role': 'assistant', 'content': '...'}` | Bot returns dict when expected None | Check empty message handling in `a_generate_reply` |
| `AssertionError: assert 'llama3.2' == 'llama3'` | Outdated model name in tests | Update test fixtures and assertions |
| `Expected mock_create to be called with...` | Incorrect parameters passed to mocked function | Update code to match expected parameters |
| `assert status["status"] == "failed"` | Error handling not marking tasks as failed | Add try/except blocks that set appropriate status |

## Continuous Improvement

The test suite should evolve alongside the codebase:

1. **Regular Audits**: Periodically review tests for brittleness or redundancy
2. **Coverage Analysis**: Use `pytest-cov` to identify untested code paths
3. **Refactoring**: Extract common test patterns into fixtures or helper functions

By following these best practices, we can maintain a robust test suite that catches regressions early while remaining easy to maintain.