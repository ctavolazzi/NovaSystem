from typing import Dict  # Import Dict from the typing module
from .port_interface import PortInterface
from .tcp_port_adapter import TCPPortAdapter
from .websocket_port_adapter import WebSocketPortAdapter
# ... (Import other protocol adapters as needed)

class PortFactory:
    """
    ... (Existing docstring remains the same)
    """

    def create_port(self, config: Dict) -> PortInterface:
        """
        ... (Existing create_port method with added WebSocket support)
        """
        protocol = config["protocol"].lower()
        if protocol == "tcp":
            return TCPPortAdapter(config)
        elif protocol == "websocket":
            return WebSocketPortAdapter(config)
        # ... (Add elif blocks for other protocols)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
