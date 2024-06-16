from abc import ABC, abstractmethod

class Observer(ABC):
    def __init__(self):
        self.is_active = True

    @abstractmethod
    def update(self, subject) -> None:
        pass

    def activate(self):
        self.is_active = True

    def deactivate(self):
        self.is_active = False

    def is_observer_active(self) -> bool:
        return self.is_active

    def handle_error(self, error: Exception):
        print(f"Observer error: {error}")

    def pre_update(self):
        pass

    def post_update(self):
        pass


# Example of a concrete observer class with expanded functionality
class AdvancedObserver(Observer):
    def __init__(self):
        super().__init__()

    def update(self, subject) -> None:
        if not self.is_active:
            return

        if subject is None:
            raise ValueError("Subject cannot be None")  # Directly raise the exception

        try:
            self.pre_update()
            # Ensure 'subject' has attribute 'state' before trying to access it
            state = getattr(subject, 'state', 'No state')  # Default value if 'state' is not present
            print(f"AdvancedObserver updated with new state: {state}")
            self.post_update()
        except Exception as e:
            self.handle_error(e)

    def pre_update(self):
        print("Preparing to update AdvancedObserver.")

    def post_update(self):
        print("AdvancedObserver update complete.")

    def handle_error(self, error: Exception):
        print(f"Error in AdvancedObserver: {error}")
        # Optionally, you can re-raise the exception if needed for tests
        raise error
