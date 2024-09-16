from port_factory import PortFactory

config = {
    "name": "MyWebSocketPort",
    "protocol": "websocket",
    "uri": "ws://localhost:8765"  # Replace with your WebSocket server URI
}

port = PortFactory().create_port(config)

# Start a separate task for the WebSocket connection 
asyncio.get_event_loop().run_until_complete(port.connect())  

# ... use port.send_data and port.receive_data as needed ...
