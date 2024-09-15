from abc import ABC, abstractmethod
from typing import Any, Dict

class PortInterface(ABC):
    """
    An abstract base class defining the interface for communication ports in the NovaSystem.

    Attributes:
        name (str): The unique name of the port.
        protocol (str): The communication protocol used by the port (e.g., "TCP", "UDP").
        status (str): The current status of the port (e.g., "CONNECTED", "DISCONNECTED").
        connected_bot (Bot): The bot object associated with this port.

    Methods:
        send_data(data, destination): Sends data to the specified destination.
        receive_data(): Receives data from the port.
        connect(): Establishes a connection to the destination.
        disconnect(): Closes the connection to the destination.
        set_router(router): Sets the router object to be used for routing messages.
        get_router(): Returns the router object associated with the port.
        get_status(): Returns the current status of the port.
    """

    def __init__(self, config: Dict):
        self.name = config["name"]
        self.protocol = config["protocol"]
        self.status = "DISCONNECTED"
        self.connected_bot = None

    @abstractmethod
    def send_data(self, data: Any, destination: str) -> None:
        pass

    @abstractmethod
    def receive_data(self) -> Any:
        pass

    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    def set_router(self, router: "Router"):  # Forward reference to Router class
        self._router = router

    def get_router(self) -> "Router":  # Forward reference to Router class
        return self._router

    def get_status(self) -> str:
        return self.status
