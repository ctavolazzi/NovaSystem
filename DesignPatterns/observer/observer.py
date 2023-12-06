from abc import ABC, abstractmethod

class Observer(ABC):
    """
    The expanded Observer class for a modular AI system. This version includes
    enhanced functionalities and handles various edge cases.
    """

    def __init__(self):
        self.is_active = True  # Determines if the observer is actively observing

    @abstractmethod
    def update(self, subject) -> None:
        """
        Abstract method that each concrete observer must implement. This method is
        called whenever the observed subject changes its state.
        """
        pass

    def activate(self):
        """
        Activates the observer, allowing it to receive and respond to updates.
        """
        self.is_active = True

    def deactivate(self):
        """
        Deactivates the observer, preventing it from receiving or responding to updates.
        """
        self.is_active = False

    def is_observer_active(self) -> bool:
        """
        Checks if the observer is active.
        Returns:
            bool: True if the observer is active, False otherwise.
        """
        return self.is_active

    def handle_error(self, error: Exception):
        """
        Handles errors that may occur during the update process. This method can be
        overridden by concrete observers to implement custom error handling.
        """
        print(f"An error occurred: {error}")

    def pre_update(self):
        """
        Optional hook method that can be overridden by concrete observers. This method
        is called before the update method.
        """
        pass

    def post_update(self):
        """
        Optional hook method that can be overridden by concrete observers. This method
        is called after the update method.
        """
        pass

# Example of a concrete observer class with expanded functionality
class AdvancedObserver(Observer):
    def update(self, subject) -> None:
        if self.is_active:
            try:
                self.pre_update()
                # Implementation of the observer's response to the state change
                print(f"AdvancedObserver updated with new state: {subject.state}")
                self.post_update()
            except Exception as e:
                self.handle_error(e)

    def pre_update(self):
        print("Preparing to update AdvancedObserver.")

    def post_update(self):
        print("AdvancedObserver update complete.")

    def handle_error(self, error: Exception):
        # Custom error handling
        print(f"Error in AdvancedObserver: {error}")
