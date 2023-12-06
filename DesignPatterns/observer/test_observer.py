import unittest
from unittest.mock import patch
from observer import Observer, AdvancedObserver

class MockSubject:
    """
    A mock subject class to simulate state changes for testing observers.
    """
    def __init__(self):
        self.state = None

    def change_state(self, new_state):
        self.state = new_state

class TestObserver(unittest.TestCase):
    """
    Test suite for the Observer class and its functionalities.
    """

    def setUp(self):
        self.subject = MockSubject()
        self.observer = AdvancedObserver()

    def test_activation(self):
        """ Test if the observer correctly activates and deactivates. """
        self.observer.deactivate()
        self.assertFalse(self.observer.is_observer_active())

        self.observer.activate()
        self.assertTrue(self.observer.is_observer_active())

    def test_update_when_active(self):
        """ Test if the observer updates its state when active. """
        with patch('sys.stdout') as mock_stdout:
            self.subject.change_state("new_state")
            self.observer.activate()
            self.observer.update(self.subject)
            self.assertIn("AdvancedObserver updated with new state: new_state", mock_stdout.getvalue())

    def test_no_update_when_inactive(self):
        """ Test if the observer does not update its state when inactive. """
        with patch('sys.stdout') as mock_stdout:
            self.subject.change_state("new_state")
            self.observer.deactivate()
            self.observer.update(self.subject)
            self.assertEqual(mock_stdout.getvalue(), "")

    def test_error_handling(self):
        """ Test the error handling in the observer. """
        with patch('sys.stdout') as mock_stdout:
            self.observer.activate()
            self.observer.update(None)  # Passing None should trigger an error in the observer
            self.assertIn("Error in AdvancedObserver", mock_stdout.getvalue())

    def test_pre_update_hook(self):
        """ Test the execution of the pre-update hook. """
        with patch('sys.stdout') as mock_stdout:
            self.observer.activate()
            self.observer.update(self.subject)
            self.assertIn("Preparing to update AdvancedObserver.", mock_stdout.getvalue())

    def test_post_update_hook(self):
        """ Test the execution of the post-update hook. """
        with patch('sys.stdout') as mock_stdout:
            self.observer.activate()
            self.observer.update(self.subject)
            self.assertIn("AdvancedObserver update complete.", mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()
