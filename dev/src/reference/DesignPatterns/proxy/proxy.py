from abc import ABC, abstractmethod
import datetime
now = datetime.datetime.now()

class Subject(ABC):
    """
    The Subject interface declares common operations for both RealSubject and the Proxy.
    """
    @abstractmethod
    def request(self) -> None:
        pass

class RealSubject(Subject):
    """
    The RealSubject contains core business logic.
    """
    def request(self) -> None:
        print("RealSubject: Handling request.")

class Proxy(Subject):
    """
    The Proxy has an interface identical to the RealSubject.
    """
    def __init__(self, real_subject: RealSubject) -> None:
        self._real_subject = real_subject

    def request(self) -> None:
        if self.check_access():
            self._real_subject.request()
            self.log_access()

    def check_access(self) -> bool:
        print("Proxy: Checking access prior to firing a real request.")
        return True

    def log_access(self) -> None:
        print("Proxy: Logging the time of request.", end="")
        print(f"Time: {now.time()}")

# Client code example
def client_code(subject: Subject) -> None:
    subject.request()

# Example usage
if __name__ == "__main__":
    real_subject = RealSubject()
    proxy = Proxy(real_subject)

    print("Client: Executing with RealSubject:")
    client_code(real_subject)

    print("\nClient: Executing with Proxy:")
    client_code(proxy)
